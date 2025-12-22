# 🎅 Santa Traditions Map (GIS Holiday Edition)

A light-hearted geospatial side project that maps **Santa Claus and his international colleagues** around the world — including **Father Frost (Ded Moroz) in Russia** — using Python and GeoPandas.

Created for fun, festive vibes, and gentle GIS humor: **color-coded traditions, oversized buffers, CRS jokes, and timezone approximations**.

> Merry Christmas and a correctly georeferenced New Year! 🎄🗺️

---

## 🌍 What’s in the Map?

* 🎅 **Multiple Santa traditions**, grouped by cultural lineage
  (Nordic, Western Europe, Slavic, Americas, Oceania, East Asia, etc.)
* 🎨 **Color-coded points by tradition**
* 🟢 **Playful “delivery influence” buffers** (300 km, purely emotional)
* ⏰ **Approximate time zones** derived from longitude
  *(Yes, we know this is not how time zones really work. That’s the joke.)*
* 📐 **CRS humor**

  * EPSG:4326 for sanity
  * EPSG:3857 for basemaps
  * North Pole geometry warnings included

---

## 🎄 Featured Locations

Some highlights:

* **Rovaniemi, Finland** — Santa Claus Village
* **Veliky Ustyug, Russia** — Father Frost (Ded Moroz) ❄️
* **New York City, USA** — last-minute delivery hub
* **Sydney, Australia** — summer Santa operations
* **Tokyo, Japan** — Hoteiosho (one eye open 👀)

…and several others.

---

## 🧰 Tech Stack

* Python 3.9+
* GeoPandas
* Matplotlib
* Shapely
* Contextily *(optional, for basemap tiles)*

---

## 🚀 How to Run

### 1. Clone the repo

```bash
git clone https://github.com/your-username/santa-traditions-map.git
cd santa-traditions-map
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install geopandas matplotlib shapely contextily pandas
```

> ⚠️ If `contextily` basemaps fail (offline / corporate network), the script will still work without tiles.

---

## ▶️ Run the script

```bash
python santa_traditions_map.py
```

This will generate:

```
santa_traditions_map.png
```

Perfect for:

* LinkedIn holiday posts
* GIS Slack channels
* Seasonal cartographic debates

---

## 🧪 Notes on Accuracy (or Lack Thereof)

* Buffers are **not** meant for analysis.
* Time zones are **longitude-based approximations**.
* Cultural locations are symbolic, not authoritative.
* Scientific rigor increases dramatically when cookies are involved.

---

## 📸 Example Output

*(Add the generated PNG here once you run the script)*

---

## 🎁 Contributing

PRs welcome if you want to add:

* More Santa traditions 🎅
* Better jokes 📐
* Worse projections 🧭

Just keep it friendly and fun.

---

## 📜 License

MIT — because Santa believes in open source.

---

## ✨ Acknowledgements

* Natural Earth for base geometries
* GeoPandas for making GIS in Python joyful
* Everyone who believes buffers should never be in degrees 🎄
