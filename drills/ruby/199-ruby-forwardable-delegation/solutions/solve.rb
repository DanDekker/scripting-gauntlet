#!/usr/bin/env ruby
# 199-ruby-forwardable-delegation — composition over inheritance with Forwardable
require "forwardable"
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

class SecureRegistry
  extend Forwardable
  def_delegators :@store, :keys, :values, :size

  attr_reader :reads

  def initialize
    @store = {}
    @reads = 0
  end

  def add(k, v)
    @store[k] = v
  end

  def lookup(k)
    @reads += 1
    @store[k]
  end
end

reg = SecureRegistry.new
rows = []
step = 0
blocked_count = 0

File.foreach(File.join(in_dir, "actions.txt")) do |line|
  text = line.strip
  next if text.empty? || text.start_with?("#")

  step += 1
  op, *args = text.split(/\s+/)

  case op
  when "add"
    reg.add(args[0], args[1].to_i)
    rows << [step, op, "ok", "#{args[0]}=#{args[1]}"]
  when "get"
    val = reg.lookup(args[0])
    rows << [step, op, "ok", val.to_s]
  when "size"
    rows << [step, op, "ok", reg.size.to_s]
  when "keys"
    rows << [step, op, "ok", reg.keys.sort.join(";")]
  when "delete"
    begin
      reg.delete(args[0])
      rows << [step, op, "ok", "deleted"]
    rescue NoMethodError
      blocked_count += 1
      rows << [step, op, "blocked", "NoMethodError"]
    end
  end
end

File.open(File.join(out_dir, "audit.csv"), "w") do |fh|
  fh.puts "step,op,status,result"
  rows.each do |r|
    fh.puts "#{r[0]},#{r[1]},#{r[2]},#{r[3]}"
  end
end

File.write(
  File.join(out_dir, "summary.json"),
  JSON.generate({
    "steps" => rows.length,
    "reads" => reg.reads,
    "blocked" => blocked_count,
    "final_size" => reg.size,
  }) + "\n"
)
