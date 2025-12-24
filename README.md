# 🎅 Santa Traditions Map (GIS Holiday Edition)

A light-hearted geospatial side project that maps **Santa Claus and his international colleagues** around the world — including **Father Frost (Ded Moroz)** — using Python and GeoPandas.

Created for festive vibes and gentle GIS humor:
**color-coded traditions, oversized buffers, CRS jokes, and timezone approximations**.

> Merry Christmas and a correctly georeferenced New Year! 🎄🗺️

---

## 🌍 What’s in the Map?

This project generates a static holiday map featuring:

* 🎅 **Multiple Santa traditions**, grouped by cultural lineage  
  *(Nordic, Western Europe, Slavic, Americas, Oceania, East Asia, etc.)*
* 🎨 **Color-coded points** representing different traditions
* 🟢 **Playful “delivery influence” buffers**  
  *(300 km, emotionally meaningful — not spatially valid)*
* ⏰ **Approximate time zones derived from longitude**  
  *(Yes, we know this is not how real time zones work. That’s the joke.)*
* 📐 **CRS humor**, including:
  * EPSG:4326 for sanity
  * EPSG:3857 for basemaps
  * North Pole geometry warnings included

---

## 🎄 Featured Locations

Some highlights from the map:

* **Rovaniemi, Finland** — Santa Claus Village
* **Veliky Ustyug, Russia** — Father Frost (Ded Moroz) ❄️
* **New York City, USA** — last-minute delivery hub
* **Sydney, Australia** — summer Santa operations
* **Tokyo, Japan** — Hoteiosho (one eye open 👀)

…and several others across the globe.

---

## 🧰 Tech Stack

* Python 3.9+
* GeoPandas
* Matplotlib
* Shapely
* Contextily *(optional — used for basemap tiles)*

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/LiubovD/Christmas_funny_map.git
cd Christmas_funny_map
