-- Plausible bug: a repeated key keeps its FIRST value, so the final report card
-- reports the stale "quarterly report" instead of "final report".
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

local function csv_field(s)
  if s:find('[,"\r\n]') then
    return '"' .. s:gsub('"', '""') .. '"'
  end
  return s
end

local values, keys = {}, {}
local duplicates, invalid = 0, 0

local fh = assert(io.open(IN .. "/report.txt", "r"))
for raw in fh:lines() do
  local line = trim(raw)
  if line ~= "" and line:sub(1, 1) ~= "#" then
    local key, value = line:match("^([^=]*)=(.*)$")
    key = key and trim(key) or ""
    if key == "" or not key:match("^[%w_.-]+$") then
      invalid = invalid + 1
    else
      value = trim(value)
      if #value >= 2 and value:sub(1, 1) == '"' and value:sub(-1) == '"' then
        value = value:sub(2, -2)
      end
      if values[key] == nil then
        keys[#keys + 1] = key
        values[key] = value
      else
        duplicates = duplicates + 1
      end
    end
  end
end
fh:close()

table.sort(keys, byte_lt)

local out = assert(io.open(OUT .. "/fields.csv", "w"))
out:write("key,value\n")
for _, key in ipairs(keys) do
  out:write(csv_field(key) .. "," .. csv_field(values[key]) .. "\n")
end
out:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format('{"keys":%d,"duplicates":%d,"invalid":%d}\n',
  #keys, duplicates, invalid))
sum:close()
