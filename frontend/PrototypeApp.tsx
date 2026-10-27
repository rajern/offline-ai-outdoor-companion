import { StatusBar } from 'expo-status-bar';
import { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator, KeyboardAvoidingView, Linking, Platform, Pressable,
  SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View,
} from 'react-native';
import { ChatResponse, ChatSource, getLocalStatus, LocalStatus, sendChatMessage } from './api';
import examples from './demo/examples.json';

type Turn = { id: number; question: string; response: ChatResponse; note?: string; label?: string };
const demoExamples = examples as { id: string; question: string; response: ChatResponse; note: string; label: string }[];

function WebLink({ url, children }: { url: string; children: string }) {
  const valid = /^https?:\/\//.test(url);
  return <Pressable accessibilityRole="link" disabled={!valid} onPress={() => void Linking.openURL(url)}>
    <Text selectable style={s.link}>{children}{valid ? ' ↗' : ''}</Text>
  </Pressable>;
}

function SourceCard({ source, index }: { source: ChatSource; index: number }) {
  const [open, setOpen] = useState(index === 0);
  return <View style={s.sourceCard}>
    <Pressable accessibilityRole="button" accessibilityState={{ expanded: open }}
      accessibilityLabel={`${open ? 'Skjul' : 'Vis'} utdrag fra ${source.title}`}
      onPress={() => setOpen(!open)} style={s.sourceHeader}>
      <Text style={s.sourceNumber}>{String(index + 1).padStart(2, '0')}</Text>
      <View style={s.grow}><Text style={s.sourceTitle}>{source.title}</Text>
        <Text style={s.small}>{source.name} · {source.excerpts.length} utdrag</Text></View>
      <Text style={s.expand}>{open ? '−' : '+'}</Text>
    </Pressable>
    {open && <View style={s.sourceBody}>
      <ScrollView nestedScrollEnabled style={s.excerptScroll}>
        {source.excerpts.map(excerpt => <View key={excerpt.id} style={s.quote}>
          <Text selectable style={s.quoteLabel}>{excerpt.section || excerpt.id} · {excerpt.language}</Text>
          <Text selectable style={s.quoteText}>«{excerpt.text}»</Text>
        </View>)}
      </ScrollView>
      <WebLink url={source.url}>Originalkilde · krever nett</WebLink>
      <Text style={s.small}>{source.content_owner || source.name}{source.retrieved_at ? ` · Hentet ${source.retrieved_at.slice(0, 10)}` : ''}</Text>
      {source.source_updated_at && <Text style={s.small}>Kilden oppdatert: {source.source_updated_at}</Text>}
      {source.licence_url ? <WebLink url={source.licence_url}>{source.license}</WebLink> : <Text style={s.small}>{source.license}</Text>}
      {source.notice && <Text style={s.small}>{source.notice}</Text>}
    </View>}
  </View>;
}

export default function PrototypeApp() {
  const [demo, setDemo] = useState(Platform.OS === 'web' && typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('demo'));
  const [turns, setTurns] = useState<Turn[]>([]);
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [pending, setPending] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<LocalStatus | null>(null);
  const [statusChecked, setStatusChecked] = useState(false);
  const scroll = useRef<ScrollView>(null);
  const revealedTurn = useRef<number | null>(null);

  async function refreshStatus() {
    setStatusChecked(false);
    try { setStatus(await getLocalStatus()); } catch { setStatus(null); }
    finally { setStatusChecked(true); }
  }
  useEffect(() => { if (!demo) void refreshStatus(); }, [demo]);

  async function submit() {
    const question = draft.trim();
    if (!question || sending || demo) return;
    setSending(true); setError(null); setPending(question); setDraft('');
    try {
      const response = await sendChatMessage(question);
      setTurns(current => [...current, { id: Date.now(), question, response }]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Kunne ikke hente svar.'); setDraft(question);
    } finally { setSending(false); setPending(''); }
  }

  function changeMode(value: boolean) { setDemo(value); setTurns([]); setError(null); setDraft(''); }
  const ready = Boolean(status?.assets_present);
  return <SafeAreaView style={s.safe}><StatusBar style="dark" />
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={s.safe}>
      <View style={s.shell}>
        <View style={s.header}><View><Text style={s.eyebrow}>LOKAL AI · ÅPNE KILDER · LÆRINGSPROTOTYPE</Text>
          <Text style={s.logo}>Outwise<Text style={s.logoDot}>.</Text></Text></View>
          <View style={[s.badge, !demo && !ready && s.badgeMuted]}><Text style={s.badgeText}>{demo ? 'Lagrede testsvar' : ready ? 'Lokale filer klare' : 'Lokalt oppsett'}</Text></View>
        </View>
        <View style={s.toolbar}>
          <View style={s.modes}>{[['Lokal modell', false], ['Se demo', true]].map(([label, value]) =>
            <Pressable key={String(label)} disabled={sending} accessibilityRole="button" accessibilityState={{ selected: demo === value }}
              onPress={() => changeMode(Boolean(value))} style={[s.mode, demo === value && s.modeActive]}>
              <Text style={[s.modeText, demo === value && s.modeTextActive]}>{String(label)}</Text>
            </Pressable>)}</View>
          <Pressable accessibilityRole="button" disabled={sending} onPress={() => { setTurns([]); setError(null); }}><Text style={s.reset}>Tøm visningen</Text></Pressable>
        </View>
        <ScrollView ref={scroll} contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
          <View style={s.intro}><Text style={s.kicker}>KUNNSKAP UTEN NETT</Text>
            <Text style={s.headline}>Se kildene.{"\n"}Vurder tolkningen.</Text>
            <Text style={s.description}>Still et spørsmål. Outwise søker i en lokal kunnskapsbase og lar en liten språkmodell forsøke å svare på norsk.</Text>
            <View style={s.flow}><Text style={s.flowText}>SPØRSMÅL  →  SØK  →  KILDER + TOLKNING</Text></View>
          </View>
          <View accessibilityRole="alert" style={s.notice}><Text style={s.noticeTitle}>Eksperimentell læringsprototype</Text>
            <Text style={s.noticeText}>Søket kan hente feil situasjon. AI-en kan utelate viktige detaljer og gi feil råd. Visningen er for å undersøke systemet; den er ikke godkjent for medisinske beslutninger eller nødsituasjoner.</Text></View>
          {demo ? <View style={s.demoPanel}><Text style={s.sectionTitle}>Utforsk et faktisk testresultat</Text>
            <Text style={s.description}>Lagrede Qwen 2B-svar fra 24. oktober 2026, med utdragene modellen fikk. Ingen modell kjøres i denne visningen.</Text>
            <View style={s.examples}>{demoExamples.map(example => <Pressable key={example.id} accessibilityRole="button"
              onPress={() => { setTurns([{ ...example, id: Date.now() }]); setError(null); }} style={s.example}>
              <Text style={s.exampleTitle}>{example.label} ↗</Text><Text style={s.small}>{example.question}</Text>
            </Pressable>)}</View></View> : <View style={s.statusPanel}>
            <Text style={s.small}>{!statusChecked ? 'Kontrollerer lokal server …' : status?.message || 'Backend svarer ikke. Start det lokale oppsettet, eller velg «Se demo».'}</Text>
            <Pressable accessibilityRole="button" onPress={() => void refreshStatus()}><Text style={s.link}>Kontroller på nytt</Text></Pressable>
          </View>}
          {turns.map(turn => <View key={turn.id} style={s.turn} onLayout={event => {
            if (turn.id === turns[turns.length - 1]?.id && revealedTurn.current !== turn.id) {
              revealedTurn.current = turn.id;
              scroll.current?.scrollTo({ y: Math.max(0, event.nativeEvent.layout.y - 12), animated: true });
            }
          }}>
            <View style={s.question}><Text style={s.questionLabel}>SPØRSMÅL</Text><Text selectable style={s.questionText}>{turn.question}</Text></View>
            {turn.note && <View style={s.review}><Text style={s.noticeTitle}>Hva testen viste</Text><Text selectable style={s.noticeText}>{turn.note}</Text></View>}
            <View style={s.resultHeading}><Text style={s.sectionTitle}>01  Hentet fra kunnskapsbasen</Text>
              <Text style={s.description}>Dette er søketreff, ikke et ferdig råd. Originalspråk og kildeopplysninger er bevart. Flere treff kan gjelde andre situasjoner.</Text></View>
            {turn.response.context_notice && <Text accessibilityRole="alert" style={s.errorText}>{turn.response.context_notice}</Text>}
            {turn.response.sources.length ? turn.response.sources.map((source, index) => <SourceCard key={`${turn.id}-${source.url}`} source={source} index={index} />)
              : <Text style={s.empty}>Ingen kildeutdrag ble hentet.</Text>}
            <View style={s.interpretation}><Text style={s.aiLabel}>02  MODELLENS TOLKNING</Text>
              <Text style={s.aiCaution}>Generert tekst · kan være feil eller ufullstendig</Text>
              <Text selectable style={s.answer}>{turn.response.answer.split(/(\*\*[^*]+\*\*)/g).map((part, index) =>
                part.startsWith('**') && part.endsWith('**') ? <Text key={index} style={{ fontWeight: '700' }}>{part.slice(2, -2)}</Text>
                  : part.replace(/^\*\s+/gm, '• '))}</Text>
              {turn.response.generation_error && <Text accessibilityRole="alert" style={s.errorText}>{turn.response.generation_error}</Text>}
            </View>
          </View>)}
          {sending && <View style={s.loading} onLayout={() => scroll.current?.scrollToEnd({ animated: true })}><ActivityIndicator color="#245D45" /><View style={s.grow}><Text style={s.sectionTitle}>Søker og lager tolkning …</Text>
            <Text style={s.small}>{pending}</Text><Text style={s.small}>Første svar kan ta tid mens modellen lastes.</Text></View></View>}
          {error && <View accessibilityRole="alert" style={s.error}><Text style={s.errorText}>{error}</Text></View>}
          <Text style={s.footer}>Kjøres på PC · Mobiltilpasset grensesnitt · Hvert spørsmål behandles separat</Text>
        </ScrollView>
        {!demo && <View style={s.composer}>
          <TextInput accessibilityLabel="Spørsmål til Outwise" placeholder="Hva vil du undersøke?" placeholderTextColor="#788179"
            multiline editable={!sending} value={draft} onChangeText={setDraft} style={s.input} />
          <Pressable accessibilityRole="button" accessibilityLabel="Send spørsmål" disabled={sending || !draft.trim()}
            onPress={() => void submit()} style={[s.send, (sending || !draft.trim()) && s.disabled]}><Text style={s.sendText}>Send ↑</Text></Pressable>
        </View>}
      </View>
    </KeyboardAvoidingView>
  </SafeAreaView>;
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#E9EDE7' }, shell: { flex: 1, width: '100%', maxWidth: 820, alignSelf: 'center', backgroundColor: '#FAFAF5', borderColor: '#D9DFD6', borderLeftWidth: 1, borderRightWidth: 1 },
  grow: { flex: 1 }, header: { paddingHorizontal: 24, paddingTop: 24, paddingBottom: 20, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 10 },
  eyebrow: { fontSize: 9, fontWeight: '700', letterSpacing: 1.1, color: '#627064', maxWidth: 230 }, logo: { fontSize: 36, fontWeight: '700', color: '#173C2D', letterSpacing: -1.8 }, logoDot: { color: '#C27D40' },
  badge: { backgroundColor: '#E0EBDC', paddingVertical: 8, paddingHorizontal: 12, borderRadius: 20 }, badgeMuted: { backgroundColor: '#EAE8DF' }, badgeText: { color: '#355139', fontSize: 11, fontWeight: '600' },
  toolbar: { paddingHorizontal: 20, paddingBottom: 16, borderBottomWidth: 1, borderColor: '#DFE3DA', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 8 }, modes: { flexDirection: 'row', backgroundColor: '#ECEFE8', padding: 4, borderRadius: 10 }, mode: { paddingVertical: 8, paddingHorizontal: 11, borderRadius: 7 }, modeActive: { backgroundColor: '#24543F' }, modeText: { color: '#59675C', fontSize: 12 }, modeTextActive: { color: '#FFF' }, reset: { color: '#637066', fontSize: 11 },
  content: { padding: 24, gap: 22, paddingBottom: 32 }, intro: { gap: 12 }, kicker: { color: '#936537', fontSize: 10, letterSpacing: 1.8, fontWeight: '700' }, headline: { fontSize: 33, lineHeight: 38, fontWeight: '600', letterSpacing: -1, color: '#193D2E' }, description: { color: '#5A665E', fontSize: 14, lineHeight: 21 }, flow: { paddingVertical: 12, borderTopWidth: 1, borderBottomWidth: 1, borderColor: '#DDE2D8' }, flowText: { fontSize: 10, letterSpacing: .7, fontWeight: '600', color: '#49604F' },
  notice: { backgroundColor: '#F3ECDD', borderLeftWidth: 3, borderLeftColor: '#B77E3E', padding: 14, gap: 5, borderRadius: 5 }, noticeTitle: { fontWeight: '700', color: '#6C522F', fontSize: 12 }, noticeText: { color: '#6A604D', fontSize: 12, lineHeight: 19 }, demoPanel: { gap: 10 }, sectionTitle: { fontWeight: '600', color: '#264C38', fontSize: 16 }, examples: { gap: 8 }, example: { padding: 14, gap: 5, backgroundColor: '#EDF1E7', borderColor: '#D7DFD0', borderWidth: 1, borderRadius: 10 }, exampleTitle: { color: '#29553C', fontWeight: '700', fontSize: 13 }, small: { color: '#6A756C', fontSize: 11, lineHeight: 17 }, statusPanel: { gap: 5 },
  turn: { gap: 12 }, question: { backgroundColor: '#244F3D', borderRadius: 12, padding: 18, gap: 7 }, questionLabel: { color: '#C0D3BD', fontSize: 9, letterSpacing: 1.3, fontWeight: '700' }, questionText: { color: '#FFFFFF', fontSize: 16, lineHeight: 24 }, review: { backgroundColor: '#F4E8DD', padding: 14, borderRadius: 8, gap: 5 }, resultHeading: { marginTop: 5, gap: 7 }, sourceCard: { borderWidth: 1, borderColor: '#D8DFD2', borderRadius: 10, backgroundColor: '#FFFFFF', overflow: 'hidden' }, sourceHeader: { flexDirection: 'row', alignItems: 'center', gap: 10, padding: 13 }, sourceNumber: { color: '#8C9C87', fontSize: 12, fontWeight: '600' }, sourceTitle: { color: '#314A37', fontSize: 13, lineHeight: 18, fontWeight: '600' }, expand: { color: '#667960', fontSize: 22 }, sourceBody: { paddingHorizontal: 14, paddingBottom: 14, gap: 7 }, excerptScroll: { maxHeight: 260 }, quote: { paddingLeft: 11, paddingBottom: 12, borderLeftWidth: 2, borderLeftColor: '#C4D3BD', gap: 5 }, quoteLabel: { color: '#7A8576', fontSize: 10 }, quoteText: { color: '#39473D', fontSize: 13, lineHeight: 21 }, link: { color: '#366447', fontSize: 11, lineHeight: 18, textDecorationLine: 'underline' }, empty: { color: '#7A7464', padding: 12, fontSize: 13 },
  interpretation: { backgroundColor: '#E9EEE4', borderRadius: 10, padding: 18, gap: 9, borderWidth: 1, borderColor: '#D4DDCC' }, aiLabel: { color: '#42603D', fontSize: 10, letterSpacing: 1, fontWeight: '700' }, aiCaution: { color: '#7F6B46', fontSize: 11 }, answer: { fontSize: 15, lineHeight: 24, color: '#26382D' },
  loading: { flexDirection: 'row', gap: 12, paddingVertical: 16 }, error: { padding: 14, backgroundColor: '#F7E5E0', borderRadius: 8 }, errorText: { color: '#873F35', fontSize: 13, lineHeight: 20 }, footer: { fontSize: 10, lineHeight: 16, color: '#889082', textAlign: 'center' }, composer: { flexDirection: 'row', gap: 10, padding: 16, borderTopWidth: 1, borderColor: '#D8DFD2', backgroundColor: '#FAFAF5', alignItems: 'flex-end' }, input: { flex: 1, backgroundColor: '#FFFFFF', borderWidth: 1, borderColor: '#CDD5C8', padding: 13, borderRadius: 10, minHeight: 48, maxHeight: 112, fontSize: 15, color: '#28392C' }, send: { backgroundColor: '#24543F', paddingHorizontal: 18, height: 48, borderRadius: 10, justifyContent: 'center' }, sendText: { color: '#FFF', fontWeight: '600', fontSize: 13 }, disabled: { opacity: .45 },
});
