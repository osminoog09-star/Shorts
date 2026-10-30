package ee.m1lash.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.net.Uri
import android.view.View
import android.widget.RemoteViews
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.text.NumberFormat
import java.time.LocalDate
import java.util.Locale
import kotlin.concurrent.thread

const val SITE = "https://osminoog09-star.github.io/Shorts/studio/"

class StudioWidget : AppWidgetProvider() {
    override fun onUpdate(ctx: Context, mgr: AppWidgetManager, ids: IntArray) = refresh(ctx)

    override fun onReceive(ctx: Context, intent: Intent) {
        super.onReceive(ctx, intent)
        if (intent.action == ACTION) refresh(ctx)
    }

    private fun refresh(ctx: Context) {
        val pending = goAsync()
        thread {
            try {
                val data = runCatching { load() }.getOrNull()
                val views = render(ctx, data)
                if (data != null) runCatching { Notifier.check(ctx, data) }
                val mgr = AppWidgetManager.getInstance(ctx)
                mgr.updateAppWidget(ComponentName(ctx, StudioWidget::class.java), views)
            } finally { pending.finish() }
        }
    }

    private fun load(): JSONObject {
        val c = URL(SITE + "data.json?t=" + System.currentTimeMillis()).openConnection() as HttpURLConnection
        c.connectTimeout = 10000; c.readTimeout = 15000; c.useCaches = false
        return c.inputStream.bufferedReader().use { JSONObject(it.readText()) }
    }

    private fun render(ctx: Context, d: JSONObject?): RemoteViews {
        val v = RemoteViews(ctx.packageName, R.layout.widget)
        val open = PendingIntent.getActivity(ctx, 0, Intent(Intent.ACTION_VIEW, Uri.parse(SITE)),
            PendingIntent.FLAG_IMMUTABLE)
        v.setOnClickPendingIntent(R.id.root, open)
        val ref = PendingIntent.getBroadcast(ctx, 1, Intent(ctx, StudioWidget::class.java).setAction(ACTION),
            PendingIntent.FLAG_IMMUTABLE)
        v.setOnClickPendingIntent(R.id.refresh, ref)
        if (d == null) { v.setTextViewText(R.id.next, "Нет связи — нажми ⟳"); return v }
        val nf = NumberFormat.getIntegerInstance(Locale("ru"))
        val ch = d.getJSONObject("channel")
        v.setTextViewText(R.id.subs, nf.format(ch.optLong("subs")))
        v.setTextViewText(R.id.total, nf.format(ch.optLong("views")))
        val daily = d.optJSONArray("daily")
        var week = 0L
        if (daily != null) for (i in maxOf(0, daily.length() - 7) until daily.length()) week += daily.getJSONObject(i).optLong("views")
        v.setTextViewText(R.id.week, nf.format(week))
        if (daily != null && daily.length() >= 14) {
            var prev = 0L
            for (i in daily.length() - 14 until daily.length() - 7) prev += daily.getJSONObject(i).optLong("views")
            if (prev > 0) {
                val pct = (week - prev) * 100 / prev
                v.setTextViewText(R.id.delta, "7 дней · " + (if (pct >= 0) "▲" else "▼") + " ${kotlin.math.abs(pct)} %")
                v.setTextColor(R.id.delta, if (pct >= 0) 0xFF5FD38D.toInt() else 0xFFFF6B6B.toInt())
            }
        }
        if (daily != null && daily.length() > 1) v.setImageViewBitmap(R.id.chart, chart(daily))
        val live = d.optJSONObject("live")
        if (live != null) {
            val r = live.optJSONArray("recent")?.optJSONObject(0)
            val h24 = live.optLong("views_24h")
            v.setTextViewText(R.id.fresh, (if (r != null) "🆕 ${r.optString("title").replace(Regex("\\s*#\\S+"), "")} — ${nf.format(r.optLong("views"))} · +${nf.format(r.optLong("views_1h"))} за час\n" else "") +
                "⏱ за 24 ч: +${nf.format(h24)} просм. · +${live.optLong("subs_24h")} подп.")
        } else v.setTextViewText(R.id.fresh, "")
        val y = d.optJSONObject("ypp")
        val base = y?.optJSONArray("tiers")?.optJSONObject(0)
        if (base != null) {
            val subsNow = if (y.has("live_subs")) y.optLong("live_subs") else base.getJSONObject("subs").optLong("current")
            val sh = base.getJSONArray("paths").getJSONObject(0)
            val pSubs = subsNow * 1000 / 500
            val pViews = (sh.optDouble("current") * 1000 / sh.optDouble("target")).toLong()
            val eta = base.optInt("eta_days", -1)
            v.setTextViewText(R.id.ypp, "💰 Монетизация: $subsNow/500 подп. · ${nf.format(sh.optLong("current"))}/3 млн Shorts" +
                (if (!base.isNull("eta_days") && eta > 0) " · ≈$eta дн" else ""))
            v.setProgressBar(R.id.ypp_bar, 1000, minOf(pSubs, pViews).toInt().coerceIn(0, 1000).coerceAtLeast(8), false)
        }
        val ev = d.optJSONObject("events")
        val top = ev?.optJSONObject("top_recent")
        v.setTextViewText(R.id.top, if (top != null) "🏆 ${top.optString("title")} — ${nf.format(top.optLong("views"))}" else "")
        val ideas = d.optJSONObject("ideas")?.optJSONArray("ideas")
        if (ideas != null && ideas.length() > 0) {
            val first = ideas.getJSONObject(0)
            v.setTextViewText(R.id.idea, "💡 Идей: ${ideas.length()} · ${first.optString("title")}")
        } else v.setTextViewText(R.id.idea, "")
        v.setTextViewText(R.id.updated, d.optString("built"))
        val review = d.optJSONArray("review")?.length() ?: 0
        if (review > 0) {
            v.setViewVisibility(R.id.review, View.VISIBLE)
            v.setTextViewText(R.id.review, "Ждёт твоего «ок»: $review")
        } else v.setViewVisibility(R.id.review, View.GONE)
        val today = LocalDate.now().toString()
        val plan = d.optJSONArray("plan")
        val lines = mutableListOf<String>()
        if (plan != null) for (i in 0 until plan.length()) {
            val p = plan.getJSONObject(i)
            if (p.optString("date") < today) continue
            val date = p.optString("date")
            val title = if (p.isNull("title")) p.optString("what") else p.optString("title")
            lines += "${date.substring(8)}.${date.substring(5, 7)} ${p.optString("time")} · $title · ${p.optString("status")}"
            if (lines.size == 3) break
        }
        v.setTextViewText(R.id.next, if (lines.isEmpty()) "Слотов нет" else lines.joinToString("\n"))
        return v
    }

    private fun chart(a: org.json.JSONArray): Bitmap {
        val n = minOf(14, a.length()); val w = 700; val h = 110
        val vals = (a.length() - n until a.length()).map { a.getJSONObject(it).optLong("views").toFloat() }
        val max = maxOf(1f, vals.maxOrNull() ?: 1f)
        val b = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888); val c = Canvas(b)
        val p = Paint(Paint.ANTI_ALIAS_FLAG); val gap = 6f; val bw = (w - gap * (n - 1)) / n
        vals.forEachIndexed { i, x ->
            p.color = if (i >= n - 7) 0xFFFF5FA8.toInt() else 0x66FF5FA8
            val top = h - maxOf(4f, x / max * (h - 4))
            c.drawRoundRect(i * (bw + gap), top, i * (bw + gap) + bw, h.toFloat(), 6f, 6f, p)
        }
        return b
    }

    companion object { const val ACTION = "ee.m1lash.widget.REFRESH" }
}
