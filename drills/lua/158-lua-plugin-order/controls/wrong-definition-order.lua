-- Plausible bug: the ready set is scanned in definition order instead of alphabetical
local IN = assert(os.getenv("IN"), "IN not set")
local OUT = assert(os.getenv("OUT"), "OUT not set")

local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local function byte_lt(a, b)
  if a == b then return false end
  for i = 1, math.min(#a, #b) do
    local ca, cb = a:byte(i), b:byte(i)
    if ca ~= cb then return ca < cb end
  end
  return #a < #b
end

local function csv_field(s)
  if s:find('[,"\r\n]') then
    return '"' .. s:gsub('"', '""') .. '"'
  end
  return s
end

local defined, deps, names = {}, {}, {}
local errors = {}

local function fail(name, reason)
  if not errors[name] then errors[name] = reason end
end

local fh = assert(io.open(IN .. "/plugins.txt", "r"))
for raw in fh:lines() do
  local line = trim(raw)
  if line ~= "" and line:sub(1, 1) ~= "#" then
    local name, rest = line:match("^([^:]*):(.*)$")
    if not name then
      name, rest = line, ""
    end
    name = trim(name)
    if defined[name] then
      fail(name, "duplicate-name")
    elseif not name:match("^[a-z0-9-]+$") then
      fail(name, "bad-name")
    else
      defined[name] = true
      names[#names + 1] = name
      local list = {}
      for piece in (rest .. ","):gmatch("([^,]*),") do
        local dep = trim(piece)
        if dep ~= "" then list[#list + 1] = dep end
      end
      deps[name] = list
    end
  end
end
fh:close()

-- dep-level failures: bad characters, then definitions that do not exist
for _, name in ipairs(names) do
  for _, dep in ipairs(deps[name]) do
    if not dep:match("^[a-z0-9-]+$") then
      fail(name, "bad-dep:" .. dep)
    elseif not defined[dep] then
      fail(name, "missing-dep:" .. dep)
    end
  end
end

-- reachability, so a plugin that reaches itself is a cycle
local reach = {}
for _, name in ipairs(names) do reach[name] = {} end
for _, name in ipairs(names) do
  for _, dep in ipairs(deps[name]) do
    if defined[dep] then reach[name][dep] = true end
  end
end
local changed = true
while changed do
  changed = false
  for _, name in ipairs(names) do
    local snapshot = {}
    for seen in pairs(reach[name]) do snapshot[#snapshot + 1] = seen end
    for _, mid in ipairs(snapshot) do
      for further in pairs(reach[mid]) do
        if not reach[name][further] then
          reach[name][further] = true
          changed = true
        end
      end
    end
  end
end
for _, name in ipairs(names) do
  if reach[name][name] then fail(name, "cycle") end
end

-- blocked cascades, so iterate until the verdicts stop changing
repeat
  changed = false
  for _, name in ipairs(names) do
    if not errors[name] then
      local worst
      for _, dep in ipairs(deps[name]) do
        if errors[dep] and (worst == nil or byte_lt(dep, worst)) then worst = dep end
      end
      if worst then
        fail(name, "blocked:" .. worst)
        changed = true
      end
    end
  end
until not changed

-- topo order: repeatedly the alphabetically smallest ready plugin
local loaded, placed = {}, {}
local pending = 0
for _, name in ipairs(names) do
  if not errors[name] then pending = pending + 1 end
end
while pending > 0 do
  local pick
  for _, name in ipairs(names) do
    if not errors[name] and not placed[name] then
      local ready = true
      for _, dep in ipairs(deps[name]) do
        if defined[dep] and not placed[dep] then ready = false break end
      end
      if ready and pick == nil then pick = name end
    end
  end
  if not pick then break end
  placed[pick] = true
  loaded[#loaded + 1] = pick
  pending = pending - 1
end

local out = assert(io.open(OUT .. "/order.csv", "w"))
out:write("position,name\n")
for index, name in ipairs(loaded) do
  out:write(string.format("%d,%s\n", index, name))
end
out:close()

local failed = {}
for _, name in ipairs(names) do
  if errors[name] then failed[#failed + 1] = name end
end
table.sort(failed, byte_lt)

local err = assert(io.open(OUT .. "/errors.csv", "w"))
err:write("name,reason\n")
for _, name in ipairs(failed) do
  err:write(string.format("%s,%s\n", csv_field(name), csv_field(errors[name])))
end
err:close()

local sum = assert(io.open(OUT .. "/summary.json", "w"))
sum:write(string.format('{"plugins":%d,"loaded":%d,"failed":%d}\n',
  #names, #loaded, #failed))
sum:close()
