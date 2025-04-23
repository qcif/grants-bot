# DNS Configuration for Postfix Mail Server

## Required DNS Records for grants.qfab.org

### 1. A Record
```
grants.qfab.org.    IN    A    <YOUR-SERVER-IP>
```
Replace `<YOUR-SERVER-IP>` with your mail server's public IP address.

### 2. MX Record
```
grants.qfab.org.    IN    MX    10    grants.qfab.org.
```
This record tells other mail servers where to deliver email for the grants.qfab.org subdomain.

### 3. PTR Record (Reverse DNS)
While not strictly required for receiving-only servers, it's recommended for better deliverability:
```
<REVERSE-IP>.in-addr.arpa.    IN    PTR    grants.qfab.org.
```
This must be configured with your hosting provider or whoever controls your reverse DNS zone.

## Verifying DNS Records

You can verify your DNS records using these commands:

1. Check A record:
```bash
dig grants.qfab.org A +short
```

2. Check MX record:
```bash
dig grants.qfab.org MX +short
```

3. Check PTR record:
```bash
dig -x <YOUR-SERVER-IP> +short
```

## Important Notes

1. DNS propagation can take up to 24-48 hours, though it's usually much faster.
2. Make sure your firewall allows incoming traffic on port 25 (SMTP).
3. Some ISPs block port 25 by default - contact your provider if necessary.
4. Since this server is receive-only, SPF, DKIM, and DMARC records are not required.
5. This configuration is specifically for the grants.qfab.org subdomain and won't interfere with any existing mail setup for qfab.org.