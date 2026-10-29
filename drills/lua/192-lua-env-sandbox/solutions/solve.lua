-- 192-lua-env-sandbox — execute untrusted expressions in restricted _ENV
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function make_sandbox()
  return {
    math = {
      abs = math.abs,
      min = math.min,
      max = math.max,
      sqrt = math.sqrt,
      floor = math.floor,
    },
    string = {
      lower = string.lower,
      upper = string.upper,
      sub = string.sub,
    },
    tonumber = tonumber,
    tostring = tostring,
    name = "alice",
    x = 10,
    y = 5,
  }
end

local results = {}
local counts = { ok = 0, runtime_error = 0, compile_error = 0 }

for line in io.lines(IN .. "/expressions.txt") do
  local text = line:gsub("^%s+", ""):gsub("%s+$", "")
  if text ~= "" and text:sub(1, 1) ~= "#" then
    local id_str, expr = text:match("^(%d+)%s*|%s*(.-)$")
    local id = tonumber(id_str)
    local env = make_sandbox()

    local fn, err = load("return (" .. expr .. ")", "expr_" .. id, "t", env)
    local status, res_str = "", ""
    if not fn then
      status = "compile_error"
      counts.compile_error = counts.compile_error + 1
    else
      local success, val = pcall(fn)
      if success then
        status = "ok"
        counts.ok = counts.ok + 1
        res_str = tostring(val)
      else
        status = "runtime_error"
        counts.runtime_error = counts.runtime_error + 1
      end
    end
    results[#results + 1] = { id, status, res_str }
  end
end

local out_csv = assert(io.open(OUT .. "/results.csv", "w"))
out_csv:write("id,status,result\n")
for _, r in ipairs(results) do
  out_csv:write(string.format("%d,%s,%s\n", r[1], r[2], r[3]))
end
out_csv:close()

local out_json = assert(io.open(OUT .. "/summary.json", "w"))
out_json:write(string.format(
  '{"expressions":%d,"ok":%d,"runtime_error":%d,"compile_error":%d}\n',
  #results, counts.ok, counts.runtime_error, counts.compile_error
))
out_json:close()
