#!/usr/bin/env ruby
# Plausible bug: divides through a float and truncates with to_i, which rounds toward
# zero instead of flooring. Negative accounts come out one cent too high.
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
  quotient = (sums[account].to_f / counts[account]).to_i
  remainder = sums[account] - quotient * counts[account]
  [account, sums[account], counts[account], quotient, remainder]
end

File.open(File.join(out_dir, "averages.csv"), "w") do |fh|
  fh.puts "account,sum,count,avg_cents,carry"
  rows.each { |row| fh.puts row.join(",") }
end

total = sums.values.sum
negative = sums.values.count(&:negative?)
File.write(File.join(out_dir, "summary.json"),
           JSON.generate({ "accounts" => accounts.length, "total" => total, "negative_accounts" => negative }) + "\n")
