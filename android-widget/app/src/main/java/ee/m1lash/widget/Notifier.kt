package ee.m1lash.widget

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.Uri
import org.json.JSONObject

/** Сравнивает свежий data.json с прошлым и шлёт уведомления о новом. */
object Notifier {
    private const val CH = "m1lash"

    fun check(ctx: Context, d: JSONObject) {
        val p = ctx.getSharedPreferences("seen", Context.MODE_PRIVATE)
        val first = !p.getBoolean("init", false)
        val e = d.optJSONObject("events") ?: JSONObject()
        val reviewIds = d.optJSONArray("review")?.let { a -> (0 until a.length()).map { a.getJSONObject(it).optString("id") } } ?: emptyList()
        val oldReview = p.getStringSet("review", emptySet()) ?: emptySet()
        val last = e.optJSONObject("last_video")
        val spike = e.optJSONObject("spike")
        val ideasDate = e.optString("ideas_date", "")
        if (!first) {
            val newReview = reviewIds.filter { it !in oldReview }
            if (newReview.isNotEmpty()) send(ctx, 1, "Ждёт твоего «ок»", "${newReview.size} ролик(а) залиты приватно — посмотри и скажи «заливаем»")
            if (last != null && last.optString("id") != p.getString("last", ""))
                send(ctx, 2, "Ролик вышел", last.optString("title"))
            if (spike != null && spike.optString("day") != p.getString("spike", ""))
                send(ctx, 3, "Всплеск просмотров 🚀", "${spike.optInt("views")} за день (обычно ~${spike.optInt("avg7")})")
            if (ideasDate.isNotEmpty() && ideasDate != p.getString("ideas", ""))
                send(ctx, 4, "Новые идеи дня", "${e.optInt("ideas_count")} идей по свежей аналитике")
        }
        val app = d.optJSONObject("app")
        val mine = runCatching { @Suppress("DEPRECATION") ctx.packageManager.getPackageInfo(ctx.packageName, 0).versionCode.toLong() }.getOrDefault(0L)
        if (app != null && app.optLong("version") > mine && app.optLong("version") != p.getLong("app", 0))
            send(ctx, 5, "Обновление виджета M1lash", "Нажми, чтобы скачать новую версию", app.optString("apk"))
        p.edit().putLong("app", app?.optLong("version") ?: 0).putBoolean("init", true).putStringSet("review", reviewIds.toSet())
            .putString("last", last?.optString("id") ?: "").putString("spike", spike?.optString("day") ?: "")
            .putString("ideas", ideasDate).apply()
    }

    private fun send(ctx: Context, id: Int, title: String, text: String, url: String = SITE) {
        val nm = ctx.getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(NotificationChannel(CH, "Студия M1lash", NotificationManager.IMPORTANCE_DEFAULT))
        val open = PendingIntent.getActivity(ctx, 10 + id, Intent(Intent.ACTION_VIEW, Uri.parse(url)), PendingIntent.FLAG_IMMUTABLE)
        val n = Notification.Builder(ctx, CH).setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title).setContentText(text).setStyle(Notification.BigTextStyle().bigText(text))
            .setContentIntent(open).setAutoCancel(true).build()
        nm.notify(id, n)
    }
}
