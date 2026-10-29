-- 004-scrape-table — lua patterns, scoped to the #pricing table.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")
os.execute("mkdir -p '" .. OUT .. "'")

local fh = assert(io.open(IN .. "/pricing.html", "r"))
local html = fh:read("a")
fh:close()

local section = html:match('<table id="pricing".-</table>')
if not section then error("pricing table not found in pricing.html") end

local function text(cell)
  cell = cell:gsub('<span class="badge">.-</span>', '')
  cell = cell:gsub('<[^>]*>', '')
  cell = cell:gsub('&amp;', '&'):gsub('&nbsp;', ' '):gsub('&lt;', '<'):gsub('&gt;', '>')
  cell = cell:gsub('%s+', ' ')
  return (cell:gsub('^ ', ''):gsub(' $', ''))
end

local plans = {}
for row in section:gmatch('<tr[^>]*>(.-)</tr>') do
  local cells = {}
  for cell in row:gmatch('<td[^>]*>(.-)</td>') do
    cells[#cells + 1] = text(cell)
  end
  if #cells >= 3 then
    local seats = tonumber(cells[2])
    local monthly = tonumber((cells[3]:gsub('[%$,]', '')))
    if seats and monthly and cells[1] ~= '' then
      plans[#plans + 1] = { name = cells[1], seats = seats, monthly = monthly }
    end
  end
end

table.sort(plans, function(a, b)
  if a.monthly ~= b.monthly then return a.monthly > b.monthly end
  return a.name < b.name
end)

local f = assert(io.open(OUT .. "/pricing.csv", "w"))
f:write("plan,seats,monthly_usd\n")
for _, plan in ipairs(plans) do
  f:write(string.format("%s,%d,%.2f\n", plan.name, plan.seats, plan.monthly))
end
f:close()
