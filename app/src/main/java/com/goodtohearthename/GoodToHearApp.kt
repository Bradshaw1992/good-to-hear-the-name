package com.goodtohearthename

import android.app.Application
import com.google.firebase.FirebaseApp
import com.google.firebase.analytics.FirebaseAnalytics

class GoodToHearApp : Application() {
    override fun onCreate() {
        super.onCreate()
        FirebaseApp.initializeApp(this)

        // Consent Mode: analytics granted (anonymised app-usage events for DAU/MAU/retention),
        // all advertising storage denied (no ad cookies/tracking ever). GDPR-defensible
        // without a consent banner because we collect no advertising data.
        val granted = FirebaseAnalytics.ConsentStatus.GRANTED
        val denied = FirebaseAnalytics.ConsentStatus.DENIED
        FirebaseAnalytics.getInstance(this).setConsent(
            mapOf(
                FirebaseAnalytics.ConsentType.ANALYTICS_STORAGE to granted,
                FirebaseAnalytics.ConsentType.AD_STORAGE to denied,
                FirebaseAnalytics.ConsentType.AD_USER_DATA to denied,
                FirebaseAnalytics.ConsentType.AD_PERSONALIZATION to denied,
            )
        )
    }
}
