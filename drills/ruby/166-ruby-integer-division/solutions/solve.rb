#!/usr/bin/env ruby
# 166-ruby-integer-division — Integer#/ floors, and divmod hands back both halves.
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

sums = Hash.new(0)
counts = Hash.new(0)

File.foreach(File.join(in_dir, "balances.csv")) do |line|
  text = line.chomp.strip
  next if text.empty? || text.start_with?("#")
  account, delta = text.split(",", 2)
  next if account == "account"
  sums[account] += Integer(delta, 10)
  counts[account] += 1
end

accounts = sums.keys.sort
rows = accounts.map do |account|
  quotient, remainder = sums[account].divmod(counts[account])
  [account, sums[account], counts[account], quotient, remainder]
end

File.open(File.join(out_dir, "averages.csv"), "w") do |fh|
  fh.puts "account,sum,count,avg_cents,carry"
  rows.each { |row| fh.puts row.join(",") }
end

total = sums.values.sum
negative = sums.values.count(&:negative?)
summary = { "accounts" => accounts.length, "total" => total, "negative_accounts" => negative }
File.write(File.join(out_dir, "summary.json"), JSON.generate(summary) + "\n")
