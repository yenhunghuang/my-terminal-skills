#!/usr/bin/env ruby
# frozen_string_literal: true

require "digest"
require "find"
require "optparse"
require "pathname"

options = { include_generated: false, duplicates: true }

OptionParser.new do |parser|
  parser.banner = "Usage: inventory_instruction_files.rb [ROOT] [options]"
  parser.on("--include-generated", "Include caches, dependencies, and build output") do
    options[:include_generated] = true
  end
  parser.on("--no-duplicates", "Do not print duplicate groups") do
    options[:duplicates] = false
  end
end.parse!

root = File.expand_path(ARGV.shift || ".")
abort("Not a directory: #{root}") unless File.directory?(root)

exact_names = %w[
  agent.md
  agents.md
  soul.md
].freeze

generated_segments = %w[
  .cache
  .git
  .mypy_cache
  .npm
  .pytest_cache
  .ruff_cache
  .tox
  .venv
  .primer-cache
  __pycache__
  build
  coverage
  dist
  node_modules
  site-packages
  target
  vendor
  venv
].freeze

generated_prefixes = []

if root == File.expand_path("~")
  generated_segments = (generated_segments + %w[
    .Trash
    Applications
    Library
    Movies
    Music
    Pictures
  ]).freeze
  generated_prefixes = %w[
    .antigravity/extensions/
    .bun/install/cache/
  ].freeze
end

template_segments = %w[
  example
  examples
  fixture
  fixtures
  template
  templates
  testdata
].freeze

def generated_path?(relative, segments, prefixes = [])
  parts = relative.split(File::SEPARATOR)
  return true if (parts & segments).any?
  return true if prefixes.any? { |prefix| relative.start_with?(prefix) }
  return true if relative.start_with?(".codex/.tmp/", ".codex/plugins/cache/")
  return true if relative.start_with?(".vscode/extensions/", ".npm/_npx/")

  relative.include?("/go/pkg/mod/") || relative.start_with?("go/pkg/mod/")
end

def owning_repository(path, root)
  current = File.dirname(path)

  loop do
    if File.exist?(File.join(current, ".git"))
      relative = Pathname.new(current).relative_path_from(Pathname.new(root)).to_s
      return relative == "." ? "." : relative
    end

    break if current == root

    parent = File.dirname(current)
    break if parent == current || !(parent == root || parent.start_with?("#{root}#{File::SEPARATOR}"))

    current = parent
  end

  "(none)"
end

def instruction_file?(relative, exact_names)
  base = File.basename(relative).downcase
  exact_names.include?(base)
end

def instruction_role(relative, template_segments)
  parts = relative.downcase.split(File::SEPARATOR)
  return "template/example" if (parts & template_segments).any?

  "entry/rule"
end

rows = []

Find.find(root) do |path|
  relative = Pathname.new(path).relative_path_from(Pathname.new(root)).to_s

  if File.directory?(path)
    git_internal = relative.split(File::SEPARATOR).include?(".git")
    if path != root && (git_internal ||
       (!options[:include_generated] &&
        generated_path?(relative, generated_segments, generated_prefixes)))
      Find.prune
    else
      next
    end
  end

  next unless File.file?(path)
  next unless instruction_file?(relative, exact_names)

  generated = generated_path?(relative, generated_segments, generated_prefixes)
  next if generated && !options[:include_generated]

  content = File.binread(path)
  rows << {
    path: relative,
    lines: content.empty? ? 0 : content.count("\n") + (content.end_with?("\n") ? 0 : 1),
    bytes: content.bytesize,
    digest: Digest::SHA256.hexdigest(content),
    scope: File.dirname(relative) == "." ? "root" : "nested",
    role: instruction_role(relative, template_segments),
    origin: generated ? "generated/third-party" : "first-party",
    repository: owning_repository(path, root)
  }
rescue Errno::EACCES, Errno::ENOENT
  warn("Skipped unreadable path: #{path}")
end

rows.sort_by! { |row| row[:path].downcase }

puts %w[lines bytes sha12 scope role origin repository path].join("\t")
rows.each do |row|
  puts [
    row[:lines],
    row[:bytes],
    row[:digest][0, 12],
    row[:scope],
    row[:role],
    row[:origin],
    row[:repository],
    row[:path]
  ].join("\t")
end

if options[:duplicates]
  duplicate_groups = rows.group_by { |row| row[:digest] }.values.select { |group| group.length > 1 }
  duplicate_groups.each do |group|
    puts "\n# duplicate #{group.first[:digest][0, 12]}"
    group.each { |row| puts row[:path] }
  end
end

warn("Found #{rows.length} instruction file(s) under #{root}")
