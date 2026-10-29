#!/usr/bin/env ruby
# Plausible bug: uses `path || "/"` which converts explicit nil to "/"
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

def build_endpoint(host:, port: 8080, path: "/", timeout: 30)
  # BUG: replaces explicit nil with default "/"
  p = path || "/"
  url = "http://#{host}:#{port}#{p}"
  t = timeout || 30
  [url, t.to_s]
end

records = JSON.parse(File.read(File.join(in_dir, "endpoints.json")))
rows = []
valid_count = 0
missing_host_count = 0
null_overrides_count = 0

records.each do |r|
  id = r["id"]
  kwargs = r.reject { |k| k == "id" }.transform_keys(&:to_sym)

  if kwargs.key?(:path) && kwargs[:path].nil? || kwargs.key?(:timeout) && kwargs[:timeout].nil?
    null_overrides_count += 1
  end

  begin
    url, t = build_endpoint(**kwargs)
    rows << [id, "valid", url, t]
    valid_count += 1
  rescue ArgumentError => e
    rows << [id, "missing_host", "", ""]
    missing_host_count += 1
  end
end

File.open(File.join(out_dir, "endpoints.csv"), "w") do |fh|
  fh.puts "id,status,url,timeout"
  rows.each do |r|
    fh.puts "#{r[0]},#{r[1]},#{r[2]},#{r[3]}"
  end
end

File.write(
  File.join(out_dir, "summary.json"),
  JSON.generate({
    "endpoints" => rows.length,
    "valid" => valid_count,
    "missing_host" => missing_host_count,
    "null_overrides" => null_overrides_count,
  }) + "\n"
)
