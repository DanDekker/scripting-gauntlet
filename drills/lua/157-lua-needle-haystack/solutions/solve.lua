-- 157-lua-needle-haystack — plain substring search over a directory tree.
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local NEEDLE = "token=100%"
local ROOT = IN .. "/corpus"

-- walk with the host's find: lua has no directory listing in its standard library
local function list_files()
  local paths = {}
  local pipe = assert(io.popen("find '" .. ROOT .. "' -type f"))
  for line in pipe:lines() do
    paths[#paths + 1] = line
  end
  local ok, how, code = pipe:close()
  if not ok and how == "exit" and code ~= 0 then
    error("find failed with exit " .. tostring(code), 0)
  end
  return paths
end

local function relative(path)
  return path:sub(#ROOT + 2)
end

local files, binary = {}, 0
for _, path in ipairs(list_files()) do
  local fh = io.open(path, "rb")
  if fh then
    local blob = fh:read("a") or ""
    fh:close()
    -- a NUL byte means binary: skip, and count it
    if blob:find("\0", 1, true) then
      binary = binary + 1
    else
      files[#files + 1] = { path = relative(path), blob = blob }
    end
  end
end

local hits = {}
for _, file in ipairs(files) do
  local number = 0
  for line in (file.blob .. "\n"):gmatch("([^\n]*)\n") do
    number = number + 1
    -- plain = true: the needle contains '%', which is a pattern escape
    local column = line:find(NEEDLE, 1, true)
    if column then
      hits[#hits + 1] = { path = file.path, line = number, column = column }
    end
  end
end

-- drop the synthetic trailing line an empty file would produce
local cleaned = {}
for _, hit in ipairs(hits) do
  cleaned[#cleaned + 1] = hit
end

table.sort(cleaned, function(a, b)
  if a.path ~= b.path then
    for i = 1, math.min(#a.path, #b.path) do
      local ca, cb = a.path:byte(i), b.path:byte(i)
      if ca ~= cb then return ca < cb end
    end
    return #a.path < #b.path
  end
  return a.line < b.line
end)

local out = assert(io.open(OUT .. "/hits.csv", "w"))
out:write("path,line,column\n")
for _, hit in ipairs(cleaned) do
  out:write(string.format("%s,%d,%d\n", hit.path, hit.line, hit.column))
end
out:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format('{"files":%d,"binary":%d,"hits":%d}\n',
  #files, binary, #cleaned))
sum:close()
