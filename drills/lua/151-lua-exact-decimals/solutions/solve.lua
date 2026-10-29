-- 151-lua-exact-decimals — integer thousandths, no floats anywhere.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local function byte_lt(a, b)
  local la, lb = #a, #b
  local n = la < lb and la or lb
  for i = 1, n do
    local ca, cb = a:byte(i), b:byte(i)
    if ca ~= cb then return ca < cb end
  end
  return la < lb
end

-- Scale a decimal string to integer thousandths, or return nil when it is not one.
local function to_thousandths(text)
  local sign, whole = text:match("^([+-]?)(%d+)$")
  local frac
  if not sign then
    sign, whole, frac = text:match("^([+-]?)(%d+)%.(%d+)$")
    if not sign or #frac > 3 then return nil end
  end
  whole = whole:gsub("^0+", "")
  if whole == "" then whole = "0" end
  frac = frac or ""
  frac = frac .. string.rep("0", 3 - #frac)
  local value = tonumber(whole) * 1000 + tonumber(frac)
  if sign == "-" then value = -value end
  return value
end

-- Print integer thousandths as a signed decimal with exactly three places.
local function scaled(v)
  local sign = ""
  if v < 0 then
    sign = "-"
    v = -v
  end
  return string.format("%s%d.%03d", sign, v // 1000, v % 1000)
end

local stats, names = {}, {}
local records, invalid = 0, 0

local fh = assert(io.open(IN .. "/measurements.csv", "r"))
local first = true
for raw in fh:lines() do
  local line = trim(raw)
  if not first then
    local sensor, value = line:match("^([^,]*),(.*)$")
    sensor = sensor and trim(sensor) or ""
    value = value and trim(value) or ""
    local scaled_value = sensor ~= "" and to_thousandths(value) or nil
    if scaled_value == nil then
      invalid = invalid + 1
    else
      records = records + 1
      local s = stats[sensor]
      if not s then
        s = { count = 0, min = scaled_value, max = scaled_value, total = 0 }
        stats[sensor] = s
        names[#names + 1] = sensor
      end
      s.count = s.count + 1
      s.total = s.total + scaled_value
      if scaled_value < s.min then s.min = scaled_value end
      if scaled_value > s.max then s.max = scaled_value end
    end
  end
  first = false
end
fh:close()

table.sort(names, byte_lt)

local total = 0
local out = assert(io.open(OUT .. "/sensors.csv", "w"))
out:write("sensor,count,min,max,total\n")
for _, name in ipairs(names) do
  local s = stats[name]
  total = total + s.total
  out:write(string.format("%s,%d,%s,%s,%s\n",
    name, s.count, scaled(s.min), scaled(s.max), scaled(s.total)))
end
out:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format('{"sensors":%d,"records":%d,"invalid":%d,"total":"%s"}\n',
  #names, records, invalid, scaled(total)))
sum:close()
