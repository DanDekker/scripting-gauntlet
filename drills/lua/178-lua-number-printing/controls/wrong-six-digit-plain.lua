-- Plausible bug: formats the plain column with %g instead of using tostring.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function trim(s) return (s:gsub("^%s+", ""):gsub("%s+$", "")) end

local rows = {}
local integers, floats, invalid, scientific = 0, 0, 0, 0

for line in io.lines(IN .. "/numbers.txt") do
  local token = trim(line)
  if token ~= "" and token:sub(1, 1) ~= "#" then
    local value = tonumber(token)
    if value == nil then
      invalid = invalid + 1
      rows[#rows + 1] = { token, "invalid", "", "", "" }
    else
      local kind = math.type(value)
      if kind == "integer" then integers = integers + 1 else floats = floats + 1 end
      local plain = string.format("%.6g", value)
      if plain:find("e", 1, true) then scientific = scientific + 1 end
      rows[#rows + 1] = {
        token, kind, plain,
        string.format("%.17g", value),
        string.format("%.6g", value),
      }
    end
  end
end

local out = assert(io.open(OUT .. "/numbers.csv", "w"))
out:write("token,kind,plain,full,short\n")
for _, row in ipairs(rows) do out:write(table.concat(row, ",") .. "\n") end
out:close()

local summary = assert(io.open(OUT .. "/summary.json", "w"))
summary:write(string.format(
  '{"rows":%d,"integers":%d,"floats":%d,"invalid":%d,"scientific":%d}\n',
  #rows, integers, floats, invalid, scientific))
summary:close()
