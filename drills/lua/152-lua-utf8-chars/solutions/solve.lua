-- 152-lua-utf8-chars — the utf8 library does the work.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function csv_field(s)
  if s:find('[,"\r\n]') then
    return '"' .. s:gsub('"', '""') .. '"'
  end
  return s
end

local lines, valid, invalid = {}, 0, 0
local total_chars, total_bytes = 0, 0

local fh = assert(io.open(IN .. "/mixed.txt", "rb"))
for line in fh:lines() do
  lines[#lines + 1] = line
end
fh:close()

local out = assert(io.open(OUT .. "/chars.csv", "w"))
out:write("line,chars,bytes,head\n")

for index, line in ipairs(lines) do
  if line ~= "" then
    -- utf8.len returns nil plus the position of the first invalid byte.
    local chars = utf8.len(line)
    if chars == nil then
      invalid = invalid + 1
    else
      valid = valid + 1
      local bytes = #line
      total_chars = total_chars + chars
      total_bytes = total_bytes + bytes
      -- byte index of the 11th character: nil when the line is shorter.
      local cut = utf8.offset(line, 11)
      local head = cut and line:sub(1, cut - 1) or line
      out:write(string.format("%d,%d,%d,%s\n", index, chars, bytes, csv_field(head)))
    end
  end
end
out:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format(
  '{"lines":%d,"valid":%d,"invalid":%d,"chars":%d,"bytes":%d}\n',
  #lines, valid, invalid, total_chars, total_bytes))
sum:close()
