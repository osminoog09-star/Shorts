package ee.m1lash.widget

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle

class OpenActivity : Activity() {
    override fun onCreate(s: Bundle?) {
        super.onCreate(s)
        startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(SITE)))
        finish()
    }
}
