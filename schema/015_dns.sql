-- 015 DNS lane (2026-09-28)
-- Captain asked to add DNS. Public domain is not cut over.
-- pianomanuel.com remains expired / not in this control plane.
-- Do not rewrite 011. BETA sqlite only.

INSERT OR REPLACE INTO meta(key, value) VALUES
('updated', '2026-09-28'),
('schema_version', '15'),
('compile_date', '2026-09-28'),
('beta_flag', 'FINAL BETA 1.04'),
('public_dns', 'off'),
('dns_lane', 'loopback'),
('dns_hub', 'https://127.0.0.1:8444/bridge.html'),
('dns_main_thing', 'https://127.0.0.1:8443/'),
('dns_intended_host', 'pianomanuel.com'),
('dns_intended_status', 'expired_not_cutover');

INSERT INTO change_log(action, approved_by, detail)
VALUES (
  'dns_lane_015',
  'Robert (chat 2026-09-28: Add dns)',
  'Added loopback DNS pointers. public_dns stays off. No GitHub Pages. No prod sqlite overwrite.'
);
