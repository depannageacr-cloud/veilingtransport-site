<?php
declare(strict_types=1);
ini_set('session.use_strict_mode', '1');
session_set_cookie_params(['secure'=>true,'httponly'=>true,'samesite'=>'Lax','path'=>'/contact/']);
session_start();
header('Cache-Control: no-store');
header('X-Robots-Tag: index, follow');
if (empty($_SESSION['token'])) { $_SESSION['token']=bin2hex(random_bytes(32)); $_SESSION['opened']=time(); }
$error=''; $sent=false;
$limits=['naam'=>120,'email'=>254,'telefoon'=>50,'kavel'=>1200,'laden'=>350,'lossen'=>350,'tijd'=>200,'bericht'=>5000];
$values=[];
foreach ($limits as $key=>$max) { $v=$_POST[$key]??''; $values[$key]=is_string($v)?trim($v):''; }
function h(string $text): string { return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
if ($_SERVER['REQUEST_METHOD']==='POST') {
    $token=$_POST['token']??'';
    if (!is_string($token) || !hash_equals($_SESSION['token'], $token) || !empty($_POST['website'])) {
        $error='Uw aanvraag kon niet worden verwerkt. Herlaad de pagina en probeer opnieuw.';
    } elseif (time()-(int)($_SESSION['opened']??time())<3) {
        $error='Controleer uw gegevens en probeer over enkele seconden opnieuw.';
    } elseif (time()-(int)($_SESSION['last_sent']??0)<60) {
        $error='Uw vorige aanvraag is net verzonden. Wacht even voordat u opnieuw verzendt.';
    } else {
        foreach ($limits as $key=>$max) { if (strlen($values[$key])>$max*4) { $error='Een veld is te lang. Kort uw bericht in.'; } }
        foreach (['naam','email','telefoon','laden','lossen','bericht'] as $key) { if ($values[$key]==='') { $error='Vul naam, e-mail, telefoon, beide adressen en uw transportvraag in.'; } }
        if (!filter_var($values['email'], FILTER_VALIDATE_EMAIL) || preg_match('/[\r\n]/', $values['email'])) { $error='Vul een geldig e-mailadres in.'; }
        if ($error==='') {
            $labels=['naam'=>'Naam','email'=>'E-mail','telefoon'=>'Telefoon','kavel'=>'Platform en kavellink','laden'=>'Afhaaladres','lossen'=>'Afleveradres','tijd'=>'Afhaaldag en tijdslot','bericht'=>'Lading en transportvraag'];
            $body="Nieuwe aanvraag via veilingtransport.be\n\n";
            foreach ($labels as $key=>$label) { $body.=$label.": ".($values[$key]!==''?$values[$key]:'Niet opgegeven')."\n\n"; }
            $headers="From: Veilingtransport ACR <website@veilingtransport.be>\r\nReply-To: ".$values['email']."\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8";
            if (mail('depannageacr@hotmail.com','Nieuwe transportaanvraag - veilingtransport.be',$body,$headers)) {
                $_SESSION['last_sent']=time(); $_SESSION['token']=bin2hex(random_bytes(32)); $sent=true; $values=array_fill_keys(array_keys($limits),'');
            } else { $error='Verzenden lukt momenteel niet. Uw aanvraag is niet verzonden. Bel ACR of gebruik WhatsApp hieronder.'; }
        }
    }
    if ($error!=='') { http_response_code(422); }
}
?>
<!doctype html><html lang="nl-BE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Transport aanvragen bij ACR | Veilingtransport</title><meta name="description" content="Vraag uw veilingtransport rechtstreeks aan bij ACR. Bezorg uw kavellink, afhaal- en afleveradres, tijdslot en laadgegevens via het formulier op veilingtransport.be."><link rel="canonical" href="https://www.veilingtransport.be/contact/"><link rel="icon" href="/favicon.svg"><link rel="stylesheet" href="/assets/veiling.css"><link rel="stylesheet" href="/assets/guides.css"><script src="/assets/guides.js" defer></script><style>.vt-contact-trap{position:absolute;left:-10000px}.vt-contact-notice{padding:20px;border:2px solid #315d34;background:#f0f6ea;margin:20px 0}.vt-contact-error{border-color:#a53523;background:#fff4ef}.vt-tool-grid input,.vt-tool-grid textarea{font-family:inherit}</style></head><body><div class="vt-site"><a class="vt-skip" href="#inhoud">Naar de inhoud</a>{{HEADER}}<main id="inhoud"><section class="vt-guide-hero"><div class="vt-wrap"><span class="vt-eyebrow">Rechtstreeks bij Veilingtransport by ACR</span><h1>Uw kavel. Uw route.<br>Vraag transport aan.</h1><p class="vt-lead">Vul hieronder uw transportvraag in. Uw aanvraag gaat rechtstreeks naar ACR en u blijft op veilingtransport.be. Prijs, uitvoering en planning bevestigen we persoonlijk.</p></div></section><div class="vt-wrap vt-guide-layout"><article class="vt-guide-body" aria-label="Transportaanvraag">
<?php if ($sent): ?><div class="vt-contact-notice" role="status"><h2>Bedankt voor uw aanvraag.</h2><p>De mailserver heeft uw aanvraag aangenomen voor verzending naar ACR. Uw rit is pas vastgelegd na onze bevestiging. Dringend of nog geen antwoord? Bel <a href="tel:+32471379064">0471 37 90 64</a>.</p></div><?php endif; ?>
<?php if ($error!==''): ?><div class="vt-contact-notice vt-contact-error" role="alert"><?=h($error)?></div><?php endif; ?>
<section class="vt-tool" style="margin-top:0"><h2>Vertel ons wat u wilt vervoeren.</h2><p>Velden met * zijn verplicht. Nog geen definitieve aankoop? Vermeld dit bij uw aanvraag.</p><form action="/contact/" method="post"><input type="hidden" name="token" value="<?=h($_SESSION['token'])?>"><div class="vt-contact-trap" aria-hidden="true"><label>Laat dit veld leeg<input name="website" tabindex="-1" autocomplete="off"></label></div><div class="vt-tool-grid">
<label>Naam *<input name="naam" autocomplete="name" maxlength="120" required value="<?=h($values['naam'])?>"></label><label>E-mailadres *<input name="email" type="email" autocomplete="email" maxlength="254" required value="<?=h($values['email'])?>"></label>
<label>Telefoonnummer *<input name="telefoon" type="tel" autocomplete="tel" maxlength="50" required value="<?=h($values['telefoon'])?>"></label><label>Afhaaldag en tijdslot<input name="tijd" maxlength="200" placeholder="Gewenste of bevestigde afhaaldag" value="<?=h($values['tijd'])?>"></label>
<label class="vt-full">Veilingplatform, kavelnummer of kavellink<input name="kavel" maxlength="1200" value="<?=h($values['kavel'])?>"></label><label>Afhaaladres *<input name="laden" maxlength="350" placeholder="Adres of plaats, postcode en land" required value="<?=h($values['laden'])?>"></label><label>Afleveradres *<input name="lossen" maxlength="350" placeholder="Adres of plaats, postcode en land" required value="<?=h($values['lossen'])?>"></label>
<label class="vt-full">Uw transportvraag *<textarea name="bericht" maxlength="5000" rows="7" required placeholder="Wat wilt u vervoeren? Vermeld aantallen, afmetingen, massa, toestand en beschikbare laad- en loshulp."><?=h($values['bericht'])?></textarea></label></div><p class="vt-small">Uw gegevens worden per e-mail naar ACR gestuurd om uw aanvraag te behandelen. Verstuur geen wachtwoorden of betaalgegevens. Foto’s kunt u rechtstreeks via WhatsApp delen.</p><button class="vt-btn" type="submit">Verzend mijn transportaanvraag</button></form></section></article><aside class="vt-guide-side"><span class="vt-eyebrow">Liever rechtstreeks contact?</span><h2>Bespreek uw transport.</h2><p>Een korte vraag of een dringende afhaaldag? Bel ACR.</p><a class="vt-btn" href="tel:+32471379064">0471 37 90 64</a><a class="vt-btn vt-outline" href="https://wa.me/32471379064">WhatsApp ↗</a><p><a href="mailto:depannageacr@hotmail.com">depannageacr@hotmail.com</a></p><p class="vt-small">Een aanvraag is vrijblijvend. Een rit, prijs en tijdslot zijn pas bevestigd wanneer ACR dit met u heeft afgesproken.</p><a href="/veilingtransport-checklist/">Bekijk de afhaalchecklist</a></aside></div></main>{{FOOTER}}{{STICKY}}</div></body></html>
