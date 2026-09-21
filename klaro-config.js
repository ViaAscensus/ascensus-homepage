/**
 * Klaro-Konfiguration für ASCENSUS (ascensus.fit)
 * Steuert die Einwilligung für Google Analytics & Google Ads
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
          'Wir nutzen Google Analytics und Google Ads, um zu verstehen, wie unsere Website genutzt wird und wie unsere Anzeigen wirken. Du entscheidest, ob Du das erlaubst.',
        learnMore: 'Einstellungen',
      },
      acceptAll: 'Alle akzeptieren',
      acceptSelected: 'Auswahl akzeptieren',
      decline: 'Ablehnen',
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
        title: 'Google Analytics',
        description:
          'Erfasst anonymisiert, wie Besucher:innen die Website nutzen, damit wir sie verbessern können.',
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
      title: 'Google Analytics',
      purposes: ['analytics'],
      cookies: [/^_ga/, /^_gid/, /^_gat/],
      onAccept: `
        gtag('consent', 'update', { analytics_storage: 'granted' });
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
