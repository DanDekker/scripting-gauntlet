#!/usr/bin/env ruby
# 182-ruby-hash-default — the block default materialises the key; a shared array does not.
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

counts = Hash.new(0)
tags = Hash.new { |store, user| store[user] = [] }
events = 0

File.foreach(File.join(in_dir, "events.txt")) do |line|
  text = line.chomp.strip
  next if text.empty? || text.start_with?("#")
  user, tag = text.split(/\s+/, 2)
  counts[user] += 1
  tags[user] << tag
  events += 1
end

users = counts.keys.sort
File.open(File.join(out_dir, "tally.csv"), "w") do |fh|
  fh.puts "user,count,tags"
  users.each { |user| fh.puts "#{user},#{counts[user]},#{tags[user].sort.join(";")}" }
end

File.write(File.join(out_dir, "summary.json"),
           JSON.generate({ "users" => users.length, "events" => events }) + "\n")
