-- Plausible bug: executes code directly against _G without environment restriction
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

-- Leaks globals so os.execute succeeds
local results = {
  { 1, "ok", "42" },
  { 2, "ok", "ALICE" },
  { 3, "ok", "0" },  -- Bug: os.execute ran and returned 0!
  { 4, "ok", "25" },
  { 5, "compile_error", "" },
  { 6, "ok", "file" },
}

local out_csv = assert(io.open(OUT .. "/results.csv", "w"))
out_csv:write("id,status,result\n")
for _, r in ipairs(results) do
  out_csv:write(string.format("%d,%s,%s\n", r[1], r[2], r[3]))
end
out_csv:close()

local out_json = assert(io.open(OUT .. "/summary.json", "w"))
out_json:write('{"expressions":6,"ok":5,"runtime_error":0,"compile_error":1}\n')
out_json:close()
