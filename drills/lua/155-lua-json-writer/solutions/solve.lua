-- 155-lua-json-writer — a JSON writer built byte by byte.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

-- JSON escaping, not lua escaping: quote, backslash, and every byte below 0x20.
local function json_string(s)
  local parts = { '"' }
  for index = 1, #s do
    local byte = s:byte(index)
    local char = s:sub(index, index)
    if char == '"' then
      parts[#parts + 1] = '\\"'
    elseif char == "\\" then
      parts[#parts + 1] = "\\\\"
    elseif byte < 0x20 then
      parts[#parts + 1] = string.format("\\u%04x", byte)
    else
      parts[#parts + 1] = char
    end
  end
  parts[#parts + 1] = '"'
  return table.concat(parts)
end

local function json_number(value)
  if value == math.floor(value) and math.abs(value) < 2 ^ 53 then
    return string.format("%d", value)
  end
  return string.format("%.6g", value)
end

-- the note is everything after the third tab, so it may contain tabs itself
local function split_record(line)
  local first = line:find("\t", 1, true)
  if not first then return nil end
  local second = line:find("\t", first + 1, true)
  if not second then return nil end
  local third = line:find("\t", second + 1, true)
  if not third then return nil end
  return line:sub(1, first - 1),
    line:sub(first + 1, second - 1),
    line:sub(second + 1, third - 1),
    line:sub(third + 1)
end

local records = {}
local invalid = 0

local fh = assert(io.open(IN .. "/records.tsv", "rb"))
local header = true
for raw in fh:lines() do
  if not header then
    local id_text, name, score_text, note = split_record(raw)
    local id = id_text and id_text:match("^%d+$") and tonumber(id_text) or nil
    local score = score_text and tonumber(score_text) or nil
    if not id or name == nil or name == "" or score == nil then
      invalid = invalid + 1
    else
      records[#records + 1] = {
        id = id,
        name = name,
        score = score,
        note = note ~= "" and json_string(note) or "null",
      }
    end
  end
  header = false
end
fh:close()

local out = assert(io.open(OUT .. "/report.json", "w"))
out:write('{"records":[')
for index, record in ipairs(records) do
  if index > 1 then out:write(",") end
  out:write(string.format('{"id":%d,"name":%s,"score":%s,"note":%s}',
    record.id, json_string(record.name), json_number(record.score), record.note))
end
out:write(string.format('],"count":%d,"invalid":%d}\n', #records, invalid))
out:close()
