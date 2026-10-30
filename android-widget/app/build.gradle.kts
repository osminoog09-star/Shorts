plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
android {
    namespace = "ee.m1lash.widget"
    compileSdk = 34
    defaultConfig { applicationId = "ee.m1lash.widget"; minSdk = 26; targetSdk = 34; versionCode = 2; versionName = "1.1" }
    buildTypes { release { isMinifyEnabled = false; signingConfig = signingConfigs.getByName("debug") } }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
