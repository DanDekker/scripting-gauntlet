-- Plausible bug: resolves with rawget on the queried layer, so inheritance is ignored.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function trim(s) return (s:gsub("^%s+", ""):gsub("%s+$", "")) end

local layers, order = {}, {}
for line in io.lines(IN .. "/layers.txt") do
  local text = trim(line)
  if text ~= "" and text:sub(1, 1) ~= "#" then
    local name = text:match("^layer%s+(%S+)$")
    if name then
      order[#order + 1] = name
      layers[name] = {}
    else
      local key, value = text:match("^([%w_]+)%s*=%s*(.-)$")
      if key then layers[order[#order]][key] = value end
    end
  end
end

-- link each layer to the one before it
for index = 2, #order do
  setmetatable(layers[order[index]], { __index = layers[order[index - 1]] })
end

local function name_of(table_value)
  for name, candidate in pairs(layers) do
    if candidate == table_value then return name end
  end
  return nil
end

local function resolve(layer_name, key)
  local current = layers[layer_name]
  while current do
    local direct = rawget(layers[layer_name], key)
    if direct ~= nil then return direct, name_of(current) end
    local mt = getmetatable(current)
    current = mt and mt.__index or nil
  end
  return nil, nil
end

local rows = {}
local resolved, absent = 0, 0
for line in io.lines(IN .. "/lookups.txt") do
  local text = trim(line)
  if text ~= "" and text:sub(1, 1) ~= "#" then
    local layer_name, key = text:match("^(%S+)%s+(%S+)$")
    local value, source = resolve(layer_name, key)
    local own = "false"
    if value == nil then
      value, source = "", "absent"
      absent = absent + 1
    else
      resolved = resolved + 1
      if source == layer_name then own = "true" end
    end
    rows[#rows + 1] = { layer_name, key, value, source, own }
  end
end

local out = assert(io.open(OUT .. "/lookups.csv", "w"))
out:write("layer,key,value,source,own\n")
for _, row in ipairs(rows) do out:write(table.concat(row, ",") .. "\n") end
out:close()

local keys = assert(io.open(OUT .. "/own_keys.csv", "w"))
keys:write("layer,keys\n")
local sorted_layers = {}
for name in pairs(layers) do sorted_layers[#sorted_layers + 1] = name end
table.sort(sorted_layers)
for _, name in ipairs(sorted_layers) do
  local own = {}
  for key in pairs(layers[name]) do own[#own + 1] = key end
  table.sort(own)
  keys:write(name .. "," .. table.concat(own, ";") .. "\n")
end
keys:close()

local summary = assert(io.open(OUT .. "/summary.json", "w"))
summary:write(string.format('{"layers":%d,"lookups":%d,"resolved":%d,"absent":%d}\n',
  #sorted_layers, #rows, resolved, absent))
summary:close()
