package ee.m1lash.widget

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.core.content.FileProvider
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

/** Скачивает новую версию APK и открывает системный установщик (одно нажатие «Установить»). */
class UpdateActivity : Activity() {
    override fun onCreate(s: Bundle?) {
        super.onCreate(s)
        val url = intent.getStringExtra("apk") ?: APK
        if (Build.VERSION.SDK_INT >= 26 && !packageManager.canRequestPackageInstalls()) {
            Toast.makeText(this, "Разреши M1lash устанавливать обновления и нажми уведомление ещё раз", Toast.LENGTH_LONG).show()
            startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:$packageName")))
            finish(); return
        }
        Toast.makeText(this, "Скачиваю обновление M1lash…", Toast.LENGTH_SHORT).show()
        thread {
            val ok = runCatching {
                val dir = File(cacheDir, "update").apply { mkdirs() }
                val f = File(dir, "m1lash.apk")
                var c = URL(url).openConnection() as HttpURLConnection
                var hops = 0
                while (c.responseCode in 300..399 && hops++ < 5) {
                    c = URL(c.getHeaderField("Location")).openConnection() as HttpURLConnection
                }
                c.inputStream.use { i -> f.outputStream().use { o -> i.copyTo(o) } }
                val uri = FileProvider.getUriForFile(this, "ee.m1lash.widget.files", f)
                startActivity(Intent(Intent.ACTION_VIEW).setDataAndType(uri, "application/vnd.android.package-archive")
                    .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK))
            }.isSuccess
            runOnUiThread {
                if (!ok) Toast.makeText(this, "Не скачалось — открою сайт", Toast.LENGTH_LONG).show()
                    .also { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(SITE))) }
                finish()
            }
        }
    }
    companion object { const val APK = "https://github.com/osminoog09-star/Shorts/releases/download/widget/m1lash-widget.apk" }
}
