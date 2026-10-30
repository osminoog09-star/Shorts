plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
android {
    namespace = "ee.m1lash.widget"
    compileSdk = 34
    defaultConfig { applicationId = "ee.m1lash.widget"; minSdk = 26; targetSdk = 34; versionCode = 9; versionName = "2.2" }
    // Постоянный ключ из секретов (иначе Android не примет обновление поверх). Без секрета — debug (только для проверки сборки).
    val ks = System.getenv("WIDGET_KEYSTORE")
    signingConfigs {
        if (ks != null) create("m1lash") {
            storeFile = file(ks); storeType = if (System.getenv("WIDGET_KEYSTORE_TYPE") == "jks") "jks" else "pkcs12"; storePassword = System.getenv("WIDGET_KEYSTORE_PASSWORD")
            keyAlias = "m1lash"; keyPassword = System.getenv("WIDGET_KEYSTORE_PASSWORD")
        }
    }
    buildTypes { release { isMinifyEnabled = false; signingConfig = signingConfigs.getByName(if (ks != null) "m1lash" else "debug") } }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}

dependencies { implementation("androidx.core:core-ktx:1.13.1") }
