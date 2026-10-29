-- 172-lua-coroutine-pipeline — chunked producer, fatal record aborts the run.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

-- producer: yields complete lines, carrying a partial line across chunk boundaries
local function stream(path)
  return coroutine.wrap(function()
    local fh = assert(io.open(path, "r"), "cannot open " .. path)
    local buf = ""
    while true do
      local chunk = fh:read(4096)
      if not chunk then break end
      buf = buf .. chunk
      while true do
        local nl = buf:find("\n", 1, true)
        if not nl then break end
        coroutine.yield(buf:sub(1, nl - 1))
        buf = buf:sub(nl + 1)
      end
    end
    if buf ~= "" then coroutine.yield(buf) end
    fh:close()
  end)
end

local totals, counts = {}, {}
local seen, processed = 0, 0

local ok, err = pcall(function()
  for line in stream(IN .. "/stream.log") do
    seen = seen + 1
    local _user, level, amount = line:match("^(%S+)%s+(%S+)%s+(%S+)%s*$")
    if not level then
      error(string.format("line %d: expected three fields", seen), 0)
    end
    local value = tonumber(amount)
    if value == nil then
      error(string.format("line %d: amount is not a number: %s", seen, amount), 0)
    end
    totals[level] = (totals[level] or 0) + value
    counts[level] = (counts[level] or 0) + 1
    processed = processed + 1
  end
end)

local levels = {}
for level in pairs(totals) do levels[#levels + 1] = level end
table.sort(levels)

local out = assert(io.open(OUT .. "/totals.csv", "w"))
out:write("level,total,count\n")
for _, level in ipairs(levels) do
  out:write(string.format("%s,%d,%d\n", level, totals[level], counts[level]))
end
out:close()

local summary = assert(io.open(OUT .. "/summary.json", "w"))
summary:write(string.format('{"lines":%d,"processed":%d,"aborted":%s,"levels":%d}\n',
  seen, processed, ok and "null" or tostring(seen), #levels))
summary:close()

if not ok then
  io.stderr:write("aborted: " .. tostring(err) .. "\n")
end
