#!/usr/bin/ruby
# Secret-safe structural audit for a local CLIProxyAPI coding-agent setup.

require "json"
require "net/http"
require "optparse"
require "uri"
require "yaml"

options = {
  config: File.join(Dir.home, ".cli-proxy-api", "config.yaml"),
  endpoint: "http://127.0.0.1:8317",
  wrappers: [],
  models: [],
  probe: false
}

OptionParser.new do |parser|
  parser.banner = "Usage: audit_setup.rb [options]"
  parser.on("--config PATH", "CLIProxyAPI YAML config") { |value| options[:config] = value }
  parser.on("--endpoint URL", "Loopback CLIProxyAPI origin") { |value| options[:endpoint] = value }
  parser.on("--wrapper PATH", "Wrapper to inspect; repeatable") { |value| options[:wrappers] << value }
  parser.on("--model ID", "Expected model ID; repeatable") { |value| options[:models] << value }
  parser.on("--probe", "Probe the local /v1/models endpoint") { options[:probe] = true }
end.parse!

failures = []
warnings = []

def report(status, message)
  puts "#{status} #{message}"
end

config_path = File.expand_path(options[:config])
downstream_key = nil

begin
  stat = File.stat(config_path)
  if stat.file?
    report("PASS", "config_regular_file=true")
  else
    failures << "config is not a regular file"
    report("FAIL", "config_regular_file=false")
  end

  private_mode = (stat.mode & 0o077).zero?
  report(private_mode ? "PASS" : "FAIL", "config_private_mode=#{private_mode}")
  failures << "config permits group/other access" unless private_mode

  config = YAML.safe_load(File.read(config_path), aliases: true)
  keys = config.is_a?(Hash) ? config["api-keys"] : nil
  valid_keys = keys.is_a?(Array) && keys.all? { |item| item.is_a?(String) && !item.empty? }
  report(valid_keys ? "PASS" : "FAIL", "api_key_entries_valid=#{valid_keys} count=#{keys.is_a?(Array) ? keys.length : 0}")
  if valid_keys && !keys.empty?
    downstream_key = keys.first
  else
    failures << "no valid downstream API key"
  end
rescue Errno::ENOENT, Errno::EACCES, Psych::Exception => error
  failures << "config read failed"
  report("FAIL", "config_read_error=#{error.class}")
end

options[:wrappers].each do |raw_path|
  path = File.expand_path(raw_path)
  begin
    stat = File.stat(path)
    private_mode = (stat.mode & 0o077).zero?
    executable = File.executable?(path)
    embedded = downstream_key && File.binread(path).include?(downstream_key)
    report(private_mode ? "PASS" : "FAIL", "wrapper_private_mode=#{private_mode} path=#{path}")
    report(executable ? "PASS" : "FAIL", "wrapper_executable=#{executable} path=#{path}")
    report(embedded ? "FAIL" : "PASS", "wrapper_embedded_secret=#{!!embedded} path=#{path}")
    failures << "wrapper mode is not private: #{path}" unless private_mode
    failures << "wrapper is not executable: #{path}" unless executable
    failures << "wrapper embeds downstream key: #{path}" if embedded
  rescue Errno::ENOENT, Errno::EACCES => error
    failures << "wrapper read failed: #{path}"
    report("FAIL", "wrapper_read_error=#{error.class} path=#{path}")
  end
end

if options[:probe]
  begin
    endpoint = URI(options[:endpoint])
    loopback_hosts = ["127.0.0.1", "localhost", "::1"]
    unless ["http", "https"].include?(endpoint.scheme) && loopback_hosts.include?(endpoint.host)
      raise ArgumentError, "non-loopback endpoint"
    end
    raise ArgumentError, "missing downstream key" if downstream_key.nil?

    models_uri = endpoint.dup
    models_uri.path = "/v1/models"
    models_uri.query = nil

    request = Net::HTTP::Get.new(models_uri)
    request["Authorization"] = "Bearer #{downstream_key}"
    http = Net::HTTP.new(models_uri.host, models_uri.port)
    http.use_ssl = models_uri.scheme == "https"
    http.open_timeout = 5
    http.read_timeout = 30
    response = http.request(request)
    parsed = JSON.parse(response.body)
    models = parsed.fetch("data", []).map { |item| item["id"] if item.is_a?(Hash) }.compact
    ok = response.code == "200"
    report(ok ? "PASS" : "FAIL", "models_http=#{response.code} count=#{models.length}")
    failures << "model probe returned HTTP #{response.code}" unless ok

    options[:models].each do |model|
      present = models.include?(model)
      report(present ? "PASS" : "FAIL", "model_present=#{present} id=#{model}")
      failures << "missing model: #{model}" unless present
    end

    metadata_request = Net::HTTP::Get.new(models_uri)
    metadata_request["Authorization"] = "Bearer #{downstream_key}"
    metadata_request["Anthropic-Version"] = "2023-06-01"
    metadata_response = http.request(metadata_request)
    metadata = JSON.parse(metadata_response.body).fetch("data", [])
    report(metadata_response.code == "200" ? "PASS" : "WARN", "anthropic_models_http=#{metadata_response.code}")
    warnings << "Anthropic-format model metadata unavailable" unless metadata_response.code == "200"
    metadata.each do |item|
      next unless item.is_a?(Hash)
      id = item["id"].to_s.gsub(/[^A-Za-z0-9._:-]/, "?")[0, 120]
      display = item["display_name"].to_s.gsub(/[^A-Za-z0-9 ._():+-]/, "?")[0, 120]
      report("INFO", "model_metadata id=#{id} display=#{display} max_input_tokens=#{item["max_input_tokens"]} max_tokens=#{item["max_tokens"]}")
    end
  rescue StandardError => error
    failures << "local model probe failed"
    report("FAIL", "probe_error=#{error.class}")
  end
end

report("INFO", "warnings=#{warnings.length} failures=#{failures.length}")
exit(failures.empty? ? 0 : 1)
