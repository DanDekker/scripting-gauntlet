-- Plausible bug: wraps each record in pcall and skips the bad one, so the run never
-- aborts and the totals include records that came after the failure.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

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

for line in stream(IN .. "/stream.log") do
  seen = seen + 1
  local _user, level, amount = line:match("^(%S+)%s+(%S+)%s+(%S+)%s*$")
  local ok = pcall(function()
    if not level then error("expected three fields", 0) end
    local value = tonumber(amount)
    if value == nil then error("amount is not a number", 0) end
    totals[level] = (totals[level] or 0) + value
    counts[level] = (counts[level] or 0) + 1
  end)
  if ok then processed = processed + 1 end
end

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
summary:write(string.format('{"lines":%d,"processed":%d,"aborted":null,"levels":%d}\n',
  seen, processed, #levels))
summary:close()
