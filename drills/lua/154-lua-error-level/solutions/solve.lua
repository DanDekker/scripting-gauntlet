-- 154-lua-error-level — raise the reason, catch it, report it unchanged.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local function csv_field(s)
  if s:find('[,"\r\n]') then
    return '"' .. s:gsub('"', '""') .. '"'
  end
  return s
end

-- error(msg, 0) raises the text with no "file:line:" prefix.
local function check(line)
  local eq = line:find("=", 1, true)
  if not eq then error("missing '='", 0) end
  local key = trim(line:sub(1, eq - 1))
  local value = trim(line:sub(eq + 1))
  if key == "" or not key:match("^[%w_-]+$") then
    error("bad key: " .. key, 0)
  end
  if not value:match("^%d+$") then
    error("not an integer: " .. value, 0)
  end
  return key, value
end

local errors, accepted = {}, {}
local seen = {}
local lines = 0

local fh = assert(io.open(IN .. "/records.txt", "r"))
for raw in fh:lines() do
  lines = lines + 1
  local line = trim(raw)
  if line ~= "" and line:sub(1, 1) ~= "#" then
    local ok, key, value = pcall(check, line)
    if not ok then
      errors[#errors + 1] = { line = lines, reason = key }
    elseif seen[key] then
      errors[#errors + 1] = { line = lines, reason = "duplicate key: " .. key }
    else
      seen[key] = true
      accepted[#accepted + 1] = { key = key, value = value }
    end
  end
end
fh:close()

local err = assert(io.open(OUT .. "/errors.csv", "w"))
err:write("line,reason\n")
for _, item in ipairs(errors) do
  err:write(string.format("%d,%s\n", item.line, csv_field(item.reason)))
end
err:close()

local acc = assert(io.open(OUT .. "/accepted.csv", "w"))
acc:write("key,value\n")
for _, item in ipairs(accepted) do
  acc:write(string.format("%s,%s\n", item.key, csv_field(item.value)))
end
acc:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format('{"lines":%d,"accepted":%d,"errors":%d}\n',
  lines, #accepted, #errors))
sum:close()
