-- Plausible bug: compiles the expression with the global environment, so os.time() runs
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local sandbox = setmetatable(
  { floor = math.floor, ceil = math.ceil, abs = math.abs,
    min = math.min, max = math.max, sqrt = math.sqrt },
  { __index = function(_, name) error("unknown name: " .. tostring(name), 0) end }
)

local PREFIX = '^%[string "expr"%]:%d+: '
local function normalise(message)
  return (tostring(message):gsub(PREFIX, ""))
end

local function evaluate(expr)
  local chunk, load_error = load("return " .. expr, "expr", "t")
  if not chunk then
    return "syntax", normalise(load_error)
  end
  local ok, value = pcall(chunk)
  if not ok then
    return "runtime", normalise(value)
  end
  if type(value) ~= "number" then
    return "not_number", tostring(value)
  end
  return "ok", tostring(value)
end

local function csv_field(text)
  text = tostring(text)
  if text:find('[,"\n]') then
    return '"' .. text:gsub('"', '""') .. '"'
  end
  return text
end

local rows, counts = {}, { ok = 0, syntax = 0, runtime = 0, not_number = 0 }

for line in io.lines(IN .. "/exprs.txt") do
  local expr = (line:gsub("^%s+", ""):gsub("%s+$", ""))
  if expr ~= "" and expr:sub(1, 1) ~= "#" then
    local status, detail = evaluate(expr)
    counts[status] = counts[status] + 1
    rows[#rows + 1] = { expr, status, detail }
  end
end

local out = assert(io.open(OUT .. "/results.csv", "w"))
out:write("expr,status,detail\n")
for _, row in ipairs(rows) do
  out:write(table.concat({ csv_field(row[1]), csv_field(row[2]), csv_field(row[3]) }, ",") .. "\n")
end
out:close()

local summary = assert(io.open(OUT .. "/summary.json", "w"))
summary:write(string.format(
  '{"lines":%d,"ok":%d,"syntax":%d,"runtime":%d,"not_number":%d}\n',
  #rows, counts.ok, counts.syntax, counts.runtime, counts.not_number))
summary:close()
