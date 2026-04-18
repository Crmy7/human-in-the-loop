// Tracking Matomo

export default defineNuxtPlugin(() => {
  const script = document.createElement("script")
  script.src = "https://analytics.bb-digital.ch/matomo.js"
  document.head.appendChild(script)

  window._paq = window._paq || []
  window._paq.push(["setSiteId", "1"])
  window._paq.push(["trackPageView"])
})
