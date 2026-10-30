package ee.m1lash.widget

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle

class OpenActivity : Activity() {
    override fun onCreate(s: Bundle?) {
        super.onCreate(s)
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission("android.permission.POST_NOTIFICATIONS") != 0) {
            requestPermissions(arrayOf("android.permission.POST_NOTIFICATIONS"), 1)
            return
        }
        open()
    }
    override fun onRequestPermissionsResult(c: Int, p: Array<out String>, r: IntArray) = open()
    private fun open() { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(SITE))); finish() }
}
