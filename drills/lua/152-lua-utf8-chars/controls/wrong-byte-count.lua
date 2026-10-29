-- Plausible bug: uses #line (bytes) where the contract asks for characters, so every
-- accented line looks longer than it is. The invalid line is still detected and
-- skipped, so the file stays valid UTF-8 and the grader can judge the rows.
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
    if utf8.len(line) == nil then
      invalid = invalid + 1
    else
      local bytes = #line
      valid = valid + 1
      total_chars = total_chars + bytes
      total_bytes = total_bytes + bytes
      local cut = utf8.offset(line, 11)
      local head = cut and line:sub(1, cut - 1) or line
      out:write(string.format("%d,%d,%d,%s\n", index, bytes, bytes, csv_field(head)))
    end
  end
end
out:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format(
  '{"lines":%d,"valid":%d,"invalid":%d,"chars":%d,"bytes":%d}\n',
  #lines, valid, invalid, total_chars, total_bytes))
sum:close()
