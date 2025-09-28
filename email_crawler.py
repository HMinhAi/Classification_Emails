import os
import re
import base64
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from Translator import Translate_txt

class EmailCrawler:
    def __init__(self, credentials_file="credentials.json", token_file="token.json"):
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
    def authenticate(self):
        """Xác thực với Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Credentials file {self.credentials_file} not found. Please download from Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        
        # Build service
        self.service = build("gmail", "v1", credentials=creds)
        return True
    
    def extract_emails(self, text):
        """Trích xuất email từ text"""
        if not text:
            return []
        emails = re.findall(self.email_pattern, text)
        return emails
    
    def get_from_header(self, headers):
        """Lấy thông tin người gửi từ headers"""
        for header in headers:
            if header.get("name") == "From":
                return header.get("value")
        return None
    
    def get_subject_header(self, headers):
        """Lấy subject từ headers"""
        for header in headers:
            if header.get("name") == "Subject":
                return header.get("value")
        return "No Subject"
    
    def decode_message_content(self, msg_payload):
        """Decode nội dung email"""
        encoded_data = None
        
        # Try to get data from parts first
        if 'parts' in msg_payload and msg_payload['parts']:
            for part in msg_payload['parts']:
                if part.get('mimeType') == 'text/plain' and 'body' in part and 'data' in part['body']:
                    encoded_data = part['body']['data']
                    break
                elif part.get('mimeType') == 'text/html' and 'body' in part and 'data' in part['body']:
                    encoded_data = part['body']['data']
                    break
        
        # If no parts or no data in parts, try direct body
        if not encoded_data and 'body' in msg_payload and 'data' in msg_payload['body']:
            encoded_data = msg_payload['body']['data']
        
        if encoded_data:
            try:
                decoded_bytes = base64.urlsafe_b64decode(encoded_data)
                decoded_data = decoded_bytes.decode("utf-8", errors="replace")
                # Clean up the text
                decoded_data = re.sub(r'(\r\n|\n|\r)', ' ', decoded_data)
                decoded_data = re.sub(r'\s+', ' ', decoded_data)  # Replace multiple spaces with single space
                return decoded_data.strip()
            except Exception as e:
                print(f"Error decoding message: {e}")
                return ""
        
        return ""
    
    def crawl_emails(self, max_results=30, translate=True):
        """
        Crawl emails from Gmail
        
        Args:
            max_results (int): Số lượng email muốn crawl
            translate (bool): Có translate sang tiếng Anh không
        
        Returns:
            pandas.DataFrame: DataFrame chứa thông tin emails
        """
        if not self.service:
            raise ValueError("Service not authenticated. Call authenticate() first.")
        
        try:
            # Get messages list
            results = self.service.users().messages().list(
                userId="me", 
                labelIds=["INBOX"], 
                maxResults=max_results
            ).execute()
            
            messages = results.get("messages", [])
            
            if not messages:
                print("No messages found.")
                return pd.DataFrame()
            
            # Prepare data structure
            data = {
                'index': [],
                'message_id': [],
                'email_from': [],
                'sender_name': [],
                'subject': [],
                'content': [],
                'content_en': []
            }
            
            print(f"Processing {len(messages)} emails...")
            
            for i, message in enumerate(messages):
                try:
                    # Get message details
                    msg = self.service.users().messages().get(
                        userId="me", 
                        id=message["id"]
                    ).execute()
                    
                    # Extract headers
                    headers = msg["payload"]["headers"]
                    from_value = self.get_from_header(headers)
                    subject = self.get_subject_header(headers)
                    
                    # Extract sender email and name
                    sender_email = ""
                    sender_name = ""
                    if from_value:
                        emails = self.extract_emails(from_value)
                        sender_email = emails[0] if emails else ""
                        
                        # Extract sender name (text before email)
                        name_match = re.match(r'^(.*?)\s*<.*@.*>', from_value)
                        if name_match:
                            sender_name = name_match.group(1).strip(' "')
                        else:
                            sender_name = sender_email.split('@')[0] if sender_email else ""
                    
                    # Decode message content
                    content = self.decode_message_content(msg["payload"])
                    
                    # Translate content if requested
                    content_en = content
                    if translate and content:
                        try:
                            print(f"Translating email {i+1}...")
                            content_en = Translate_txt(content)
                        except Exception as e:
                            print(f"Translation failed for email {i+1}: {e}")
                            content_en = content
                    
                    # Add to data
                    data['index'].append(i)
                    data['message_id'].append(message["id"])
                    data['email_from'].append(sender_email)
                    data['sender_name'].append(sender_name)
                    data['subject'].append(subject)
                    data['content'].append(content)
                    data['content_en'].append(content_en)
                    
                    print(f"Processed email {i+1}/{len(messages)}: {sender_email}")
                    
                except Exception as e:
                    print(f"Error processing email {i+1}: {e}")
                    continue
            
            # Create DataFrame
            df = pd.DataFrame(data)
            return df
            
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Unexpected error: {e}")
            return pd.DataFrame()
    
    def save_to_csv(self, df, filename="crawled_emails.csv"):
        """Lưu DataFrame ra file CSV"""
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    

def main():
    """Demo function"""
    # Initialize crawler
    crawler = EmailCrawler()
    
    try:
        # Authenticate
        print("Authenticating with Gmail...")
        crawler.authenticate()
        print("Authentication successful!")
        
        # Crawl emails
        print("Crawling emails...")
        df = crawler.crawl_emails(max_results=10, translate=True)
        
        if not df.empty:
            print(f"Successfully crawled {len(df)} emails")
            print("\nSample data:")
            print(df.head())            
            
            # Save to CSV
            crawler.save_to_csv(df, "crawled_emails.csv")
        else:
            print("No emails found or error occurred")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()