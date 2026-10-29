-- 153-lua-sort-ties — table.sort is not stable, so the index rides along.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local records, invalid = {}, 0

local fh = assert(io.open(IN .. "/scores.txt", "r"))
for raw in fh:lines() do
  local line = trim(raw)
  if line ~= "" and line:sub(1, 1) ~= "#" then
    local name, digits = line:match("^(%S+)%s+(%d+)$")
    if not name then
      invalid = invalid + 1
    else
      records[#records + 1] = {
        name = name,
        score = tonumber(digits),
        index = #records + 1,
      }
    end
  end
end
fh:close()

-- score descending, then input order: the index makes the tie-break explicit.
table.sort(records, function(a, b)
  if a.score ~= b.score then return a.score > b.score end
  return a.index < b.index
end)

local out = assert(io.open(OUT .. "/sorted.csv", "w"))
out:write("name,score,index\n")
for _, record in ipairs(records) do
  out:write(string.format("%s,%d,%d\n", record.name, record.score, record.index))
end
out:close()

local counts = {}
for _, record in ipairs(records) do
  counts[record.score] = (counts[record.score] or 0) + 1
end
local tied = 0
for _, record in ipairs(records) do
  if counts[record.score] > 1 then tied = tied + 1 end
end

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format('{"records":%d,"invalid":%d,"tied":%d}\n',
  #records, invalid, tied))
sum:close()
