-- 001-csv-rollup — lua with the standard library only.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")
os.execute("mkdir -p '" .. OUT .. "'")

local function trim(s)
  return (s:gsub("%s+$", ""):gsub("^%s+", ""))
end

local function title(s)
  s = trim(s)
  return (s:gsub("^%l", string.upper))
end

-- order_id -> latest version of the row
local latest = {}
local fh = assert(io.open(IN .. "/orders.csv", "r"))
for raw in fh:lines() do
  local line = raw:gsub("\r", "")
  local f = {}
  for field in (line .. ","):gmatch("(.-),") do f[#f + 1] = field end
  local id = trim(f[1] or "")
  if id ~= "" and id:lower() ~= "order_id" then
    local ts = trim(f[6] or "")
    if (not latest[id]) or ts > latest[id].updated_at then
      latest[id] = {
        region = trim(f[3] or ""),
        status = trim(f[4] or ""):lower(),
        amount = trim(f[5] or ""),
        updated_at = ts,
      }
    end
  end
end
fh:close()

local regions, names = {}, {}
local orders, dropped, revenue = 0, 0, 0.0
for _, row in pairs(latest) do
  if row.status == "paid" then
    local raw = row.amount:gsub("%$", ""):gsub(",", "")
    local amount = tonumber(raw)
    if not amount then
      dropped = dropped + 1
    else
      local name = title(row.region)
      if not regions[name] then
        regions[name] = { count = 0, total = 0.0 }
        names[#names + 1] = name
      end
      regions[name].count = regions[name].count + 1
      regions[name].total = regions[name].total + amount
      orders = orders + 1
      revenue = revenue + amount
    end
  end
end

-- revenue desc, then region asc
table.sort(names, function(a, b)
  local ra, rb = regions[a], regions[b]
  if ra.total ~= rb.total then return ra.total > rb.total end
  return a < b
end)

local out = assert(io.open(OUT .. "/regions.csv", "w"))
out:write("region,orders,revenue\n")
for _, name in ipairs(names) do
  out:write(string.format("%s,%d,%.2f\n", name, regions[name].count, regions[name].total))
end
out:close()

local s = assert(io.open(OUT .. "/summary.json", "w"))
s:write(string.format('{"orders":%d,"regions":%d,"revenue":%.2f,"dropped":%d}\n',
  orders, #names, revenue, dropped))
s:close()
