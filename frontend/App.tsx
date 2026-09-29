import { StatusBar } from 'expo-status-bar';
import { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

import { sendChatMessage } from './api';

type Message = {
  id: number;
  role: 'assistant' | 'user';
  text: string;
};

const initialMessages: Message[] = [
  {
    id: 1,
    role: 'assistant',
    text: 'Beskriv situasjonen din. Jeg hjelper deg med å prioritere hva du bør gjøre først.',
  },
];

export default function App() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [draft, setDraft] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitMessage = async () => {
    const message = draft.trim();
    if (!message || isSending) {
      return;
    }

    setMessages((current) => [
      ...current,
      { id: Date.now(), role: 'user', text: message },
    ]);
    setDraft('');
    setError(null);
    setIsSending(true);

    try {
      const answer = await sendChatMessage(message);
      setMessages((current) => [
        ...current,
        { id: Date.now() + 1, role: 'assistant', text: answer },
      ]);
    } catch {
      setError('Kunne ikke kontakte den lokale Outwise-serveren. Kontroller at backend kjører.');
    } finally {
      setIsSending(false);
    }
  };

  const canSend = draft.trim().length > 0 && !isSending;

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.keyboardView}
      >
        <View style={styles.shell}>
          <View style={styles.header}>
            <View>
              <Text style={styles.eyebrow}>OFFLINE AI OUTDOOR COMPANION</Text>
              <Text style={styles.title}>Outwise</Text>
            </View>
            <View style={styles.status}>
              <View style={styles.statusDot} />
              <Text style={styles.statusText}>Lokalt</Text>
            </View>
          </View>

          <ScrollView
            contentContainerStyle={styles.messages}
            keyboardShouldPersistTaps="handled"
          >
            <Text style={styles.dateLabel}>NY SAMTALE</Text>

            {messages.map((message) => {
              const isUser = message.role === 'user';
              return (
                <View
                  key={message.id}
                  style={[
                    styles.messageBubble,
                    isUser ? styles.userBubble : styles.assistantBubble,
                  ]}
                >
                  <Text style={[styles.senderLabel, isUser && styles.userSenderLabel]}>
                    {isUser ? 'DEG' : 'OUTWISE'}
                  </Text>
                  <Text style={[styles.messageText, isUser && styles.userMessageText]}>
                    {message.text}
                  </Text>
                </View>
              );
            })}

            {isSending && (
              <View style={[styles.messageBubble, styles.assistantBubble, styles.loadingBubble]}>
                <ActivityIndicator color="#39734C" size="small" />
                <Text style={styles.loadingText}>Outwise svarer …</Text>
              </View>
            )}

            {error && (
              <View accessibilityRole="alert" style={styles.errorCard}>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}
          </ScrollView>

          <View style={styles.composer}>
            <TextInput
              accessibilityLabel="Beskriv situasjonen"
              editable={!isSending}
              multiline
              onChangeText={setDraft}
              onSubmitEditing={() => void submitMessage()}
              placeholder="Beskriv hva som har skjedd …"
              placeholderTextColor="#6D756F"
              style={styles.input}
              value={draft}
            />
            <TouchableOpacity
              accessibilityLabel="Send melding"
              accessibilityRole="button"
              disabled={!canSend}
              onPress={() => void submitMessage()}
              style={[styles.sendButton, !canSend && styles.sendButtonDisabled]}
            >
              <Text style={styles.sendButtonText}>Send</Text>
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#E9EDE7',
  },
  keyboardView: {
    flex: 1,
  },
  shell: {
    flex: 1,
    width: '100%',
    maxWidth: 480,
    alignSelf: 'center',
    backgroundColor: '#F8F7F1',
    borderColor: '#D8DDD6',
    borderLeftWidth: Platform.OS === 'web' ? 1 : 0,
    borderRightWidth: Platform.OS === 'web' ? 1 : 0,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 24,
    paddingBottom: 18,
    borderBottomWidth: 1,
    borderBottomColor: '#D8DDD6',
  },
  eyebrow: {
    color: '#657267',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 1.2,
  },
  title: {
    marginTop: 3,
    color: '#163A2C',
    fontSize: 30,
    fontWeight: '700',
    letterSpacing: -0.8,
  },
  status: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 7,
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 999,
    backgroundColor: '#DDE8DE',
  },
  statusDot: {
    width: 7,
    height: 7,
    borderRadius: 999,
    backgroundColor: '#39734C',
  },
  statusText: {
    color: '#244E35',
    fontSize: 12,
    fontWeight: '700',
  },
  messages: {
    flexGrow: 1,
    paddingHorizontal: 16,
    paddingVertical: 20,
    gap: 14,
  },
  dateLabel: {
    alignSelf: 'center',
    marginBottom: 2,
    color: '#7A817B',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 1.1,
  },
  messageBubble: {
    maxWidth: '86%',
    padding: 14,
    borderRadius: 16,
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#E4EAE3',
    borderBottomLeftRadius: 4,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#1E513B',
    borderBottomRightRadius: 4,
  },
  senderLabel: {
    marginBottom: 6,
    color: '#42604E',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1,
  },
  userSenderLabel: {
    color: '#CFE1D3',
  },
  messageText: {
    color: '#202A24',
    fontSize: 16,
    lineHeight: 23,
  },
  userMessageText: {
    color: '#FFFFFF',
  },
  loadingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  loadingText: {
    color: '#42604E',
    fontSize: 14,
  },
  errorCard: {
    padding: 12,
    borderWidth: 1,
    borderColor: '#CC9A91',
    borderRadius: 12,
    backgroundColor: '#F8E9E5',
  },
  errorText: {
    color: '#7A3025',
    fontSize: 13,
    lineHeight: 19,
  },
  composer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 10,
    padding: 14,
    borderTopWidth: 1,
    borderTopColor: '#D8DDD6',
    backgroundColor: '#F8F7F1',
  },
  input: {
    flex: 1,
    minHeight: 48,
    maxHeight: 112,
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: '#BFC8BF',
    borderRadius: 14,
    backgroundColor: '#FFFFFF',
    color: '#202A24',
    fontSize: 15,
    lineHeight: 21,
  },
  sendButton: {
    minHeight: 48,
    justifyContent: 'center',
    paddingHorizontal: 18,
    borderRadius: 14,
    backgroundColor: '#1E513B',
  },
  sendButtonDisabled: {
    backgroundColor: '#8A988F',
  },
  sendButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
});
