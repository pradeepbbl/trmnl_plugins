import datetime as dt

SUBUNIT_LABEL = {"EUR": "ct/kWh", "GBP": "p/kWh"}

CURRENCY_SYMBOL = {
  "EUR": "€",
  "GBP": "£",
  "SEK": "kr",
  "NOK": "kr",
  "DKK": "kr",
  "PLN": "zł",
  "CZK": "Kč",
  "HUF": "Ft",
  "RON": "lei",
  "BGN": "лв",
  "CHF": "CHF",
}

DEFAULT_USAGES = [
  ("Dishwasher (eco)", 1.0),
  ("Washing machine", 0.8),
  ("Watch TV, 1 hr", 0.1),
  ("Charge an EV", 45.0),
]

ICON_KEYWORDS = [
  ("shower", "shower"),
  ("bath", "bath"),
  ("dishwash", "dishwasher"),
  ("wash", "washer"),
  ("dryer", "dryer"),
  ("dry", "dryer"),
  ("pizza", "oven"),
  ("oven", "oven"),
  ("bake", "oven"),
  ("kettle", "kettle"),
  ("boil", "kettle"),
  ("ev", "car"),
  ("car", "car"),
  ("tv", "tv"),
  ("fridge", "fridge"),
  ("refrigerator", "fridge"),
  ("phone", "phone"),
]


def _icon_for(label):
  lower = label.lower()
  for keyword, icon in ICON_KEYWORDS:
    if keyword in lower:
      return icon
    return "bolt"


def _zone(iana, utc_offset):
  if iana:
    try:
      from zoneinfo import ZoneInfo
      return ZoneInfo(iana)
    except Exception:
      pass
    return dt.timezone(dt.timedelta(seconds=int(utc_offset or 0)))


def _round(value, digits):
  return None if value is None else round(value + 0.0, digits)


def _trim(number):
  text = ("%.2f" % number).rstrip("0").rstrip(".")
  return text or "0"


def _money(amount):
  if amount < 0:
    return "-" + _money(-amount)
    if 0 < amount < 0.01:
      return "<0.01"
  return "%.2f" % amount


def _usage_list(setting):
  parsed = []
  for line in str(setting or "").splitlines():
    line = line.strip()
    if not line or "=" not in line:
      continue
      label, _, kwh = line.rpartition("=")
    try:
      parsed.append((label.strip(), float(kwh.strip().replace(",", "."))))
    except ValueError:
      continue
    return parsed or DEFAULT_USAGES


def _empty(message, detail=None):
  return {
    "ok": False,
    "error": message,
    "error_detail": detail,
    "hours": [],
    "stats": {},
    "tomorrow": {"available": False},
    "usages": [],
    "best_time": "",
    "currency_symbol": "",
    "unit_label": "",
    "currency": "",
    "vat_percent": 0,
    "date_label": "",
    "updated_at": "",
    "zone_label": "",
  }


def run(input):
  try:
    return _run(input)
  except Exception as e:
    return _empty("Transform error", str(e))


def _run(input):
  settings = input if isinstance(input, dict) else {}
  trmnl = settings.get("trmnl") or {}
  user = trmnl.get("user") or {}
  plugin_settings = trmnl.get("plugin_settings")
  fields = (plugin_settings.get("custom_fields_values") if isinstance(plugin_settings, dict) else None) or {}

  tzinfo = _zone(user.get("time_zone_iana"), user.get("utc_offset"))
  now_local = dt.datetime.now(dt.timezone.utc).astimezone(tzinfo)

  # The API returns pre-processed JSON with zone, hours[], stats{}
  zone_label = settings.get("zone_label") or ""
  currency = settings.get("currency") or "EUR"
  raw_hours = settings.get("hours") or []
  api_stats = settings.get("stats") or {}

  if not raw_hours:
    return _empty("No price data")

    # ---- unit + tax conversion ------------------------------------------
    unit_choice = str(fields.get("price_unit") or "currency_kwh")
  symbol = CURRENCY_SYMBOL.get(currency, currency)
  try:
    vat = float(fields.get("vat_percent") or 0)
  except (TypeError, ValueError):
    vat = 0.0
    vat_factor = 1.0 + vat / 100.0

  if unit_choice == "subunit_kwh":
    # price_kwh * 100 -> cents per kWh
    def convert(h):
      return h["price_kwh"] * 100.0 * vat_factor
      unit_label = SUBUNIT_LABEL.get(currency, "c/kWh")
    digits = 2
    prefix = ""
    bare = False
  elif unit_choice == "currency_mwh":
    def convert(h):
      return h["price_mwh"] * vat_factor
      unit_label = "%s/MWh" % currency
    digits = 1
    prefix = ""
    bare = False
  else:
    # currency per kWh (default)
    def convert(h):
      return h["price_kwh"] * vat_factor
      unit_label = "%s/kWh" % symbol
    digits = 3
    prefix = symbol
    bare = True

    def digits_of(value):
      text = ("%%.%df" % digits) % abs(value)
      return text[1:] if bare and text.startswith("0.") else text

  def plain(value):
    if value is None:
      return "--"
      return "%s%s" % ("-" if value < 0 else "", digits_of(value))

    def fmt(value):
      if value is None:
        return "--"
        return "%s%s%s" % ("-" if value < 0 else "", prefix, digits_of(value))

  # ---- slice today and tomorrow from the hours array ------------------
  today_date = now_local.date()
  today_entries = []
  tomorrow_entries = []

  for h in raw_hours:
    ts = h.get("timestamp", "")
    try:
      utc_dt = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
      continue
      local_dt = utc_dt.astimezone(tzinfo)
    price = convert(h)
    if local_dt.date() == today_date:
      today_entries.append((local_dt, price, h))
    elif local_dt.date() == today_date + dt.timedelta(days=1):
      tomorrow_entries.append((local_dt, price, h))

    if not today_entries:
      return _empty("No prices for today")

  values = [price for _, price, _ in today_entries]
  low, high = min(values), max(values)
  baseline = min(0.0, low)
  span = (high - baseline) or 1.0
  current_hour = now_local.replace(minute=0, second=0, microsecond=0)

  min_index = next(i for i, (_, price, _) in enumerate(today_entries) if price == low)
  max_index = next(i for i, (_, price, _) in enumerate(today_entries) if price == high)

  hours = []
  for index, (local, price, raw) in enumerate(today_entries):
    hours.append({
      "hour": local.hour,
      "label": "%02d" % local.hour,
      "time": local.strftime("%H:%M"),
      "price": _round(price, digits),
      "display": plain(price),
      "pct": max(2, int(round((price - baseline) / span * 100))),
      "negative": price < 0,
      "is_now": local == current_hour,
      "is_past": local < current_hour,
      "is_min": index == min_index,
      "is_max": index == max_index,
    })

    now_entry = next((h for h in hours if h["is_now"]), None)
  cheapest = next(h for h in hours if h["is_min"])
  priciest = next(h for h in hours if h["is_max"])

  avg = sum(values) / len(values)
  stats = {
    "min": _round(low, digits),
    "max": _round(high, digits),
    "avg": _round(avg, digits),
    "min_display": fmt(low),
    "max_display": fmt(high),
    "avg_display": fmt(avg),
    "min_time": cheapest["time"],
    "max_time": priciest["time"],
    "now": now_entry["price"] if now_entry else None,
    "now_display": fmt(now_entry["price"]) if now_entry else "--",
    "now_time": now_entry["time"] if now_entry else now_local.strftime("%H:%M"),
    "zero_pct": int(round((0.0 - baseline) / span * 100)) if baseline < 0 else 0,
    "avg_pct": int(round((avg - baseline) / span * 100)),
    "has_negative": baseline < 0,
  }

  # ---- tomorrow stats -------------------------------------------------
  tomorrow_values = [price for _, price, _ in tomorrow_entries]
  if len(tomorrow_values) >= 20:
    t_low, t_high = min(tomorrow_values), max(tomorrow_values)
    t_avg = sum(tomorrow_values) / len(tomorrow_values)
    tomorrow_stats = {
      "available": True,
      "min_display": fmt(t_low),
      "max_display": fmt(t_high),
      "avg_display": fmt(t_avg),
    }
  else:
    tomorrow_stats = {"available": False}

    # ---- usage costs ----------------------------------------------------
    money_factor = vat_factor / 1000.0  # currency/MWh -> currency/kWh
  now_raw_mwh = next(
    (h["price_mwh"] for local, _, h in today_entries if local == current_hour),
    today_entries[0][2]["price_mwh"],
  )
  ahead = [(local, h["price_mwh"]) for local, _, h in today_entries if local >= current_hour]
  best_local, best_raw_mwh = min(ahead or [(today_entries[0][0], today_entries[0][2]["price_mwh"])], key=lambda p: p[1])

  usages = []
  for label, kwh in _usage_list(fields.get("usage_examples")):
    usages.append({
      "label": label,
      "icon": _icon_for(label),
      "kwh": _trim(kwh),
      "now": _money(kwh * now_raw_mwh * money_factor),
      "best": _money(kwh * best_raw_mwh * money_factor),
    })

    return {
      "ok": True,
      "error": None,
      "hours": hours,
      "stats": stats,
      "tomorrow": tomorrow_stats,
      "usages": usages,
      "best_time": best_local.strftime("%H:%M"),
      "currency_symbol": CURRENCY_SYMBOL.get(currency, currency),
      "unit_label": unit_label,
      "currency": currency,
      "vat_percent": vat,
      "date_label": now_local.strftime("%a %-d %b"),
      "updated_at": now_local.strftime("%H:%M"),
      "zone_label": zone_label or fields.get("bidding_zone", ""),
    }
