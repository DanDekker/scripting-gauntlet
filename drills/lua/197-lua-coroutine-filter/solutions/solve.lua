-- 197-lua-coroutine-filter — stateful stream aggregation via coroutines
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function make_meter(threshold)
  return coroutine.create(function(first_delta)
    local total = first_delta
    while true do
      local delta = coroutine.yield(total >= threshold, total)
      if not delta then break end
      total = total + delta
    end
    return total >= threshold, total
  end)
end

local meters = {}
local streams = {}
local rows = {}
local alerts_count = 0
local step = 0
local final_max = 0

for line in io.lines(IN .. "/events.txt") do
  local text = line:gsub("^%s+", ""):gsub("%s+$", "")
  if text ~= "" and text:sub(1, 1) ~= "#" then
    step = step + 1
    local stream, delta_str = text:match("^(%S+)%s+(%d+)$")
    local delta = tonumber(delta_str)

    if not meters[stream] then
      meters[stream] = make_meter(50)
      streams[stream] = true
    end

    local ok, alert, sum = coroutine.resume(meters[stream], delta)
    if alert then alerts_count = alerts_count + 1 end
    if sum > final_max then final_max = sum end

    rows[#rows + 1] = { step, stream, delta, sum, alert and "true" or "false" }
  end
end

local stream_count = 0
for _ in pairs(streams) do stream_count = stream_count + 1 end

local out_csv = assert(io.open(OUT .. "/meter.csv", "w"))
out_csv:write("step,stream,delta,sum,alert\n")
for _, r in ipairs(rows) do
  out_csv:write(string.format("%d,%s,%d,%d,%s\n", r[1], r[2], r[3], r[4], r[5]))
end
out_csv:close()

local out_json = assert(io.open(OUT .. "/summary.json", "w"))
out_json:write(string.format(
  '{"events":%d,"streams":%d,"alerts":%d,"final_max":%d}\n',
  #rows, stream_count, alerts_count, final_max
))
out_json:close()
