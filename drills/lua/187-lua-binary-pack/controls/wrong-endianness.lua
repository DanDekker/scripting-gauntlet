-- Plausible bug: uses little-endian unpack, misinterpreting msg_id and header
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local f = assert(io.open(IN .. "/stream.bin", "rb"))
local data = f:read("*a")
f:close()

-- Little-endian format <I2 <I4 unpacks wrong IDs
local frames = {
  { 9999, "corrupt_checksum", 0, "" }
}

local out_csv = assert(io.open(OUT .. "/frames.csv", "w"))
out_csv:write("msg_id,status,len,payload\n")
for _, r in ipairs(frames) do
  out_csv:write(string.format("%d,%s,%d,%s\n", r[1], r[2], r[3], r[4]))
end
out_csv:close()

local out_json = assert(io.open(OUT .. "/summary.json", "w"))
out_json:write('{"frames":1,"valid":0,"corrupt_checksum":1,"bad_magic":0,"truncated":0}\n')
out_json:close()
