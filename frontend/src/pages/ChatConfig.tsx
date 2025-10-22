import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Save, Loader2, CheckCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const ChatConfig = () => {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [currentWebhookUrl, setCurrentWebhookUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/chat/config`);
      if (response.ok) {
        const data = await response.json();
        if (data.webhook_url) {
          setCurrentWebhookUrl(data.webhook_url);
          setWebhookUrl(data.webhook_url);
        }
      }
    } catch (error) {
      console.error('Error loading config:', error);
      toast({
        title: 'Error',
        description: 'Failed to load configuration',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!webhookUrl.trim()) return;

    setIsSaving(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/chat/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ webhook_url: webhookUrl }),
      });

      if (response.ok) {
        setCurrentWebhookUrl(webhookUrl);
        toast({
          title: 'Success!',
          description: 'n8n webhook URL has been updated',
        });
      } else {
        throw new Error('Failed to update configuration');
      }
    } catch (error) {
      console.error('Error saving config:', error);
      toast({
        title: 'Error',
        description: 'Failed to save configuration',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-dark p-6">
      <div className="max-w-3xl mx-auto">
        <Button
          variant="ghost"
          onClick={() => navigate('/')}
          className="mb-6 text-white hover:bg-white/10"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Home
        </Button>

        <Card className="shadow-elegant">
          <CardHeader>
            <CardTitle className="text-3xl font-light tracking-wide">
              Chatbot Configuration
            </CardTitle>
            <CardDescription>
              Configure the n8n webhook URL for the chatbot integration
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-[#FF2D55]" />
              </div>
            ) : (
              <form onSubmit={handleSave} className="space-y-6">
                <div>
                  <Label htmlFor="webhook-url" className="text-lg">
                    n8n Webhook URL
                  </Label>
                  <p className="text-sm text-muted-foreground mb-2">
                    Enter your n8n workflow webhook URL. The chatbot will send user messages to this endpoint.
                  </p>
                  <Input
                    id="webhook-url"
                    type="url"
                    placeholder="https://your-n8n-instance.com/webhook/chat"
                    value={webhookUrl}
                    onChange={(e) => setWebhookUrl(e.target.value)}
                    required
                    className="mt-1"
                  />
                </div>

                {currentWebhookUrl && (
                  <div className="bg-muted p-4 rounded-lg">
                    <div className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-dusty-red mt-0.5" />
                      <div className="flex-1">
                        <p className="font-medium">Currently Configured</p>
                        <p className="text-sm text-muted-foreground break-all mt-1">
                          {currentWebhookUrl}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="bg-accent/50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">n8n Workflow Setup Instructions:</h4>
                  <ol className="text-sm space-y-2 list-decimal list-inside text-muted-foreground">
                    <li>Create a new workflow in n8n</li>
                    <li>Add a Webhook trigger node</li>
                    <li>Configure your workflow to process incoming messages</li>
                    <li>
                      Your workflow will receive:
                      <ul className="ml-6 mt-1 list-disc">
                        <li><code>session_id</code> - Unique chat session ID</li>
                        <li><code>user_name</code> - User's name</li>
                        <li><code>user_email</code> - User's email</li>
                        <li><code>message</code> - User's message</li>
                        <li><code>timestamp</code> - Message timestamp</li>
                      </ul>
                    </li>
                    <li>
                      Your workflow must return a JSON response with:
                      <ul className="ml-6 mt-1 list-disc">
                        <li><code>{`{"response": "Your bot's reply message"}`}</code></li>
                      </ul>
                    </li>
                    <li>Copy the webhook URL and paste it above</li>
                  </ol>
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 bg-gradient-to-r from-[#FF2D55] via-[#FF1744] to-[#E91E63] hover:shadow-lg hover:shadow-[#FF2D55]/50 transition-all duration-300 rounded-xl font-semibold"
                  disabled={isSaving || !webhookUrl.trim()}
                >
                  {isSaving ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5 mr-2" />
                      Save Configuration
                    </>
                  )}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>

        <Card className="mt-6 shadow-elegant">
          <CardHeader>
            <CardTitle className="text-xl font-light">Testing the Chatbot</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              After configuring the webhook URL, you can test the chatbot by clicking the chat button
              on the home page. The chatbot will:
            </p>
            <ul className="text-sm space-y-2 list-disc list-inside text-muted-foreground ml-4">
              <li>Collect user name and email before starting the conversation</li>
              <li>Send each message to your n8n workflow</li>
              <li>Display the response from n8n back to the user</li>
              <li>Store conversation history for each session</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ChatConfig;
