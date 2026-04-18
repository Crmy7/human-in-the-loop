// Tracking Matomo BB® — instance analytics.bb-digital.ch
// source: bb-tracking-matomo-setup.md

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const siteId = config.public.matomoSiteId

  // Désactivé si pas de siteId (ex. dev local sans MATOMO_SITE_ID)
  if (!siteId || siteId === "0") return

  const script = document.createElement("script")
  script.async = true
  script.src = "https://analytics.bb-digital.ch/matomo.js"
  document.head.appendChild(script)

  window._paq = window._paq || []
  window._paq.push(["setTrackerUrl", "https://analytics.bb-digital.ch/matomo.php"])
  window._paq.push(["setSiteId", siteId])
  window._paq.push(["trackPageView"])
  window._paq.push(["enableLinkTracking"])
})
