-- 187-lua-binary-pack — parse binary packet stream using string.unpack
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local f = assert(io.open(IN .. "/stream.bin", "rb"))
local data = f:read("*a")
f:close()

local pos = 1
local frames = {}
local counts = {
  valid = 0,
  corrupt_checksum = 0,
  bad_magic = 0,
  truncated = 0,
}

while pos <= #data do
  if pos + 6 > #data + 1 then
    -- Not enough bytes for magic + msg_id
    counts.truncated = counts.truncated + 1
    frames[#frames + 1] = { 0, "truncated", 0, "" }
    break
  end

  local magic, msg_id = string.unpack(">I2 I4", data, pos)
  if magic ~= 0xCAFE then
    -- Bad magic: attempt to read payload & advance
    local ok, _, _, payload, _, next_pos = pcall(string.unpack, ">I2 I4 s2 I1", data, pos)
    if ok then
      counts.bad_magic = counts.bad_magic + 1
      frames[#frames + 1] = { msg_id, "bad_magic", #payload, payload }
      pos = next_pos
    else
      counts.truncated = counts.truncated + 1
      frames[#frames + 1] = { msg_id, "truncated", 0, "" }
      break
    end
  else
    -- Valid magic: unpack payload and checksum
    local ok, _, _, payload, cksum, next_pos = pcall(string.unpack, ">I2 I4 s2 I1", data, pos)
    if not ok then
      counts.truncated = counts.truncated + 1
      frames[#frames + 1] = { msg_id, "truncated", 0, "" }
      break
    end

    local sum = 0
    for i = 1, #payload do
      sum = (sum + payload:byte(i)) % 256
    end

    if sum == cksum then
      counts.valid = counts.valid + 1
      frames[#frames + 1] = { msg_id, "valid", #payload, payload }
    else
      counts.corrupt_checksum = counts.corrupt_checksum + 1
      frames[#frames + 1] = { msg_id, "corrupt_checksum", #payload, payload }
    end
    pos = next_pos
  end
end

local out_csv = assert(io.open(OUT .. "/frames.csv", "w"))
out_csv:write("msg_id,status,len,payload\n")
for _, r in ipairs(frames) do
  out_csv:write(string.format("%d,%s,%d,%s\n", r[1], r[2], r[3], r[4]))
end
out_csv:close()

local out_json = assert(io.open(OUT .. "/summary.json", "w"))
out_json:write(string.format(
  '{"frames":%d,"valid":%d,"corrupt_checksum":%d,"bad_magic":%d,"truncated":%d}\n',
  #frames, counts.valid, counts.corrupt_checksum, counts.bad_magic, counts.truncated
))
out_json:close()
