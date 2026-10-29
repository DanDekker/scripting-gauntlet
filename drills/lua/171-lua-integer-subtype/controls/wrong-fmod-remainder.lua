-- Plausible bug: uses math.fmod for the remainder, which truncates instead of flooring.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function trim(s) return (s:gsub("^%s+", ""):gsub("%s+$", "")) end

local function tokens(path)
  local list = {}
  for line in io.lines(path) do
    local t = trim(line)
    if t ~= "" and t:sub(1, 1) ~= "#" then list[#list + 1] = t end
  end
  return list
end

local rows, integers, floats, invalid = {}, 0, 0, 0

for _, token in ipairs(tokens(IN .. "/values.txt")) do
  local value = tonumber(token)
  if value == nil then
    invalid = invalid + 1
    rows[#rows + 1] = { token, "invalid", "", "", "" }
  else
    local kind = math.type(value)
    if kind == "integer" then integers = integers + 1 else floats = floats + 1 end
    rows[#rows + 1] = {
      token,
      kind,
      tostring(value // 7),
      tostring(math.fmod(value, 7)),
      tostring(math.fmod(value, 7)),
    }
  end
end

local out = assert(io.open(OUT .. "/values.csv", "w"))
out:write("token,kind,quotient,remainder,fmod\n")
for _, row in ipairs(rows) do out:write(table.concat(row, ",") .. "\n") end
out:close()

local total, wrapped = 0, false
for _, token in ipairs(tokens(IN .. "/counters.txt")) do
  local value = tonumber(token)
  if value and math.type(value) == "integer" then
    local next_total = total + value
    -- overflow: adding a positive to a non-negative turned the sum negative
    if value > 0 and next_total < total then wrapped = true end
    total = next_total
  end
end

local counters = assert(io.open(OUT .. "/counters.csv", "w"))
counters:write("total,total_hex,wrapped\n")
counters:write(string.format("%d,%s,%s\n", total, string.format("%x", total), tostring(wrapped)))
counters:close()

local summary = assert(io.open(OUT .. "/summary.json", "w"))
summary:write(string.format('{"rows":%d,"integers":%d,"floats":%d,"invalid":%d}\n',
  #rows, integers, floats, invalid))
summary:close()
