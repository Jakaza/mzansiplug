# ✅ TODO List: Web Performance Optimization



## 🔤 Font Display

- [ ] **Set `font-display` property** to `swap` or `optional` to ensure consistent text visibility.
  - This reduces layout shifts when fonts load.
  - Target file:
    - `fonts/bootstrap-icons.woff2`  
      *(pub-0324bcfe1aad402d8432e0e33dd00337.r2.dev)*

---

## 🎨 CSS Optimization

### 🧹 Reduce Unused CSS  
**Estimated savings:** *364 KiB*

- [ ] Eliminate unused CSS rules, especially for above-the-fold content.
- Target files:
  - `css/bootstrap-icons.css`
  - `css/bootstrap.min_v0.1.css`
  - `css/templatemo-topic-listing_v0.1.css`

### 🧼 Minify CSS  
**Estimated savings:** *87 KiB*

- [ ] Minify CSS to reduce payload size.
- Target files:
  - `css/bootstrap.min_v0.1.css`
  - `css/bootstrap-icons.css`
  - `css/templatemo-topic-listing_v0.1.css`

---

## 📜 JavaScript Optimization

### 🧼 Minify JavaScript  
**Estimated savings:** *117 KiB*

- [ ] Minify JS to reduce payload size and parsing time.
- Target files:
  - `js/jquery.min.js`
  - `js/bootstrap.bundle.min.js`
  - `js/jquery.sticky.js`

### 🚫 Reduce Unused JavaScript  
**Estimated savings:** *415 KiB*

- [ ] Defer or remove unused JS to reduce network activity and improve load times.
- [ ] Load scripts only when needed.

---

## 🖼️ Image Optimization

### 💤 Defer Offscreen Images

- [ ] Implement lazy-loading for offscreen/hidden images to reduce Time to Interactive (TTI).

### 🕒 Use Efficient Cache Lifetimes  
**Estimated savings:** *3,660 KiB*

- [ ] Optimize cache headers for images to avoid repeated downloads.
- Target images:
  - `images/hero-background-picture.png`
  - `mzansiplug-logo-s.png`

---

## 🌐 Network & Server

### ⏱️ Reduce Document Request Latency

- [ ] Minimize latency of first network request.
  - Avoid redirects.
  - Enable text compression (e.g., GZIP/Brotli).
  - Improve server response time.
  - ⚠️ *Current observed latency: 782 ms*

