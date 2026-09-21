/**
 * Klaro-Konfiguration für ASCENSUS (ascensus.fit)
 * Steuert die Einwilligung für Google Analytics, Microsoft Clarity & Google Ads
 * und meldet die Entscheidung an Google Consent Mode v2 zurück.
 */
var klaroConfig = {
  version: 1,
  elementID: 'klaro',
  styling: {
    theme: ['light'],
  },

  // Banner erscheint automatisch beim ersten Besuch
  noAutoLoad: false,

  // Kleines Banner unten rechts (nicht als zentriertes Modal)
  noticeAsModal: false,
  htmlTexts: true,

  // Eigener Cookie-Name für die Einwilligungs-Entscheidung selbst
  cookieName: 'ascensus_consent',
  cookieExpiresAfterDays: 365,

  // Nichts ist vorausgewählt – echtes Opt-in
  default: false,
  mustConsent: false,
  acceptAll: true,
  hideDeclineAll: false,
  hideLearnMore: false,

  translations: {
    de: {
      consentModal: {
        title: 'Datenschutzeinstellungen',
        description:
          'Hier kannst Du sehen und festlegen, welche Dienste wir auf ascensus.fit verwenden dürfen. Du kannst Deine Auswahl jederzeit über den Link „Datenschutzeinstellungen" im Footer ändern.',
      },
      consentNotice: {
        description:
          'Wir nutzen Google Analytics, Microsoft Clarity und Google Ads, um zu verstehen, wie unsere Website genutzt wird und wie unsere Anzeigen wirken. Du entscheidest, ob Du das erlaubst.',
        learnMore: 'Einstellungen',
      },
      acceptAll: 'Alle akzeptieren',
      acceptSelected: 'Auswahl akzeptieren',
      decline: 'Ablehnen',
      ok: 'Okay',
      close: 'Schließen',
      purposes: {
        analytics: 'Statistik & Reichweitenmessung',
        marketing: 'Marketing & Werbe-Erfolgsmessung',
      },
      purposeItem: {
        service: 'Dienst',
        services: 'Dienste',
      },
      'google-analytics': {
        title: 'Google Analytics & Microsoft Clarity',
        description:
          'Erfasst anonymisiert, wie Besucher:innen die Website nutzen (Statistik) und wie sie sich auf der Seite bewegen (Klick-/Scroll-Verhalten), damit wir sie verbessern können.',
      },
      'google-ads': {
        title: 'Google Ads',
        description:
          'Misst, ob ein Besuch über eine unserer Google-Anzeigen zustande kam, damit wir unsere Kampagnen sinnvoll einsetzen.',
      },
    },
  },

  services: [
    {
      name: 'google-analytics',
      title: 'Google Analytics & Microsoft Clarity',
      purposes: ['analytics'],
      cookies: [/^_ga/, /^_gid/, /^_gat/, /^_clck/, /^_clsk/],
      onAccept: `
        gtag('consent', 'update', { analytics_storage: 'granted' });

        // Microsoft Clarity nur nach Zustimmung laden
        if (!window.clarity) {
          (function(c,l,a,r,i,t,y){
            c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
          })(window, document, "clarity", "script", "ylp87mc5i4");
        }
      `,
      onDecline: `
        gtag('consent', 'update', { analytics_storage: 'denied' });
      `,
    },
    {
      name: 'google-ads',
      title: 'Google Ads',
      purposes: ['marketing'],
      cookies: [],
      onAccept: `
        gtag('consent', 'update', {
          ad_storage: 'granted',
          ad_user_data: 'granted',
          ad_personalization: 'granted'
        });
      `,
      onDecline: `
        gtag('consent', 'update', {
          ad_storage: 'denied',
          ad_user_data: 'denied',
          ad_personalization: 'denied'
        });
      `,
    },
  ],
};
