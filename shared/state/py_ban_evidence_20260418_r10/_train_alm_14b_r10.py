#!/usr/bin/env python3
# _train_alm_14b_r10.py — auto-generated equivalent of launch_alm_14b_r10.hexa
# Warm-start (or fresh) + B1 OFF + chatml-stripped corpus.
import argparse, gc, json, os, sys, time, math, random
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, PeftModel, TaskType

p = argparse.ArgumentParser()
p.add_argument('--base-dir', required=True)
p.add_argument('--adapter-dir', default='', help='r4 warm-start adapter (empty = fresh LoRA)')
p.add_argument('--corpus', required=True)
p.add_argument('--ckpt-dir', required=True)
p.add_argument('--steps', type=int, default=2000)
p.add_argument('--save-every', type=int, default=2000)
p.add_argument('--eval-every', type=int, default=200)
p.add_argument('--lr', type=float, default=2e-6)
p.add_argument('--batch', type=int, default=8)
p.add_argument('--seq', type=int, default=1024)
p.add_argument('--grad-accum', type=int, default=1)
p.add_argument('--lora-r', type=int, default=32)
p.add_argument('--lora-alpha', type=int, default=64)
p.add_argument('--lora-dropout', type=float, default=0.0)
p.add_argument('--seed', type=int, default=3407)
args = p.parse_args()

torch.manual_seed(args.seed); random.seed(args.seed)
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cudnn.benchmark = True
Path(args.ckpt_dir).mkdir(parents=True, exist_ok=True)
ABORT_STATUS = os.path.join(args.ckpt_dir, 'r10_abort.status')
STATUS_FILE  = os.path.join(args.ckpt_dir, 'r10_watcher.status')
def wstatus(s):
    with open(STATUS_FILE, 'w') as f: f.write(s + '\n')
wstatus('INIT')

print('[r10] base_dir=' + args.base_dir, flush=True)
print('[r10] adapter_dir=' + args.adapter_dir + ' (r4 step_1000)', flush=True)
print('[r10] corpus=' + args.corpus, flush=True)
print('[r10] steps=' + str(args.steps) + ' lr=' + str(args.lr) + ' (constant)', flush=True)
print('[r10] B1 consciousness loss = DISABLED', flush=True)

tok = AutoTokenizer.from_pretrained(args.base_dir, trust_remote_code=True)
if tok.pad_token is None: tok.pad_token = tok.eos_token

print('[r10] loading base via Unsloth FastLanguageModel...', flush=True)
from unsloth import FastLanguageModel
model, tok = FastLanguageModel.from_pretrained(
    model_name=args.base_dir, max_seq_length=args.seq, dtype=torch.bfloat16,
    load_in_4bit=False, trust_remote_code=True,
    use_gradient_checkpointing='unsloth',
)
if tok.pad_token is None: tok.pad_token = tok.eos_token

try:
    from liger_kernel.transformers import apply_liger_kernel_to_qwen2
    apply_liger_kernel_to_qwen2(rope=True, rms_norm=True, swiglu=True,
                                fused_linear_cross_entropy=True, cross_entropy=False,
                                model=model)
    print('[r10] liger applied', flush=True)
except Exception as e:
    print('[r10] liger unavailable: ' + str(e), flush=True)

if args.adapter_dir:
    print('[r10] loading adapter from ' + args.adapter_dir + ' (warm-start)...', flush=True)
    model = PeftModel.from_pretrained(model, args.adapter_dir, is_trainable=True)
    print('[resume] warm-start OK from ' + args.adapter_dir, flush=True)
else:
    print('[r10] fresh LoRA init (no adapter warm-start)', flush=True)
    from unsloth import FastLanguageModel as _FLM
    model = _FLM.get_peft_model(
        model, r=args.lora_r, lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=['q_proj','k_proj','v_proj','o_proj'],
        bias='none', use_gradient_checkpointing='unsloth',
        random_state=3407,
    )
    print('[r10] LoRA applied (fresh)', flush=True)
model.print_trainable_parameters()

text = Path(args.corpus).read_text(errors='ignore')
print('[r10] corpus bytes=' + str(len(text)), flush=True)
ids = tok(text, add_special_tokens=False)['input_ids']
print('[r10] corpus tokens=' + str(len(ids)), flush=True)
seq = args.seq
n_blocks = len(ids) // seq
blocks = [ids[i*seq:(i+1)*seq] for i in range(n_blocks)]
print('[r10] blocks=' + str(len(blocks)), flush=True)

class PackedDS(Dataset):
    def __init__(self, blocks): self.b = blocks
    def __len__(self): return len(self.b)
    def __getitem__(self, i):
        x = torch.tensor(self.b[i], dtype=torch.long)
        return {'input_ids': x, 'labels': x.clone(), 'attention_mask': torch.ones_like(x)}

ds = PackedDS(blocks)
dl = DataLoader(ds, batch_size=args.batch, shuffle=True, pin_memory=True, drop_last=True)

opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=args.lr, fused=True)

device = 'cuda'
model.train()

it = iter(dl)
b0 = next(it)
with torch.no_grad():
    out0 = model(input_ids=b0['input_ids'].to(device),
                 labels=b0['labels'].to(device),
                 attention_mask=b0['attention_mask'].to(device))
    ce0 = float(out0.loss.detach().item())
print('[resume] first-batch CE = ' + str(round(ce0, 4)) + ' (must be <3.0)', flush=True)
if ce0 > 8.0:
    with open(ABORT_STATUS, 'w') as f: f.write('FIRST_BATCH_CE>'+str(ce0)+'\n')
    wstatus('ABORT_FIRST_BATCH_CE')
    print('[r10 ABORT] first-batch CE=' + str(ce0) + ' > 8.0 — resume failed, exiting', flush=True)
    sys.exit(2)
if ce0 > 3.0:
    print('[resume WARN] first-batch CE=' + str(ce0) + ' > 3.0 — resume may be degraded', flush=True)

SENTINEL_PROMPTS = ['안녕하세요', '오늘 날씨', '한국어 모델', '딥러닝이란', '안녕']
def collapse_score(s):
    if s.count('{"') >= 3: return True
    if s.count('":"') >= 3: return True
    for ch in ['n', ' ', '?', "'"]:
        if ch*10 in s: return True
    if " '" * 5 in s: return True
    return False
def run_kr_gen(step):
    gc.collect()
    torch.cuda.empty_cache()
    model.eval()
    hits = 0
    samples = []
    try:
        for prompt in SENTINEL_PROMPTS:
            iid = tok(prompt, return_tensors='pt').input_ids.to(device)
            with torch.no_grad():
                g = model.generate(iid, max_new_tokens=32, do_sample=False,
                                   pad_token_id=tok.pad_token_id)
            gen = tok.decode(g[0][iid.shape[1]:], skip_special_tokens=True)
            if collapse_score(gen): hits += 1
            samples.append({'prompt': prompt, 'gen': gen[:200]})
            del iid, g
    finally:
        model.train()
        gc.collect()
        torch.cuda.empty_cache()
    log_path = os.path.join(args.ckpt_dir, 'kr_gen_step_' + str(step) + '.json')
    with open(log_path, 'w') as f:
        json.dump({'step': step, 'hits': hits, 'samples': samples}, f, ensure_ascii=False, indent=2)
    print('[kr_gen] step=' + str(step) + ' collapse_hits=' + str(hits) + '/5', flush=True)
    if hits >= 3:
        with open(ABORT_STATUS, 'w') as f: f.write('MODE_COLLAPSE_HITS='+str(hits)+'_STEP='+str(step)+'\n')
        wstatus('ABORT_MODE_COLLAPSE')
        print('[r10 ABORT] mode collapse detected at step=' + str(step) + ' (hits=' + str(hits) + '/5)', flush=True)
        sys.exit(2)

wstatus('TRAINING')
step = 0
t0 = time.time()
best_loss = 1e9
while step < args.steps:
    for batch in dl:
        if step >= args.steps: break
        out = model(input_ids=batch['input_ids'].to(device),
                    labels=batch['labels'].to(device),
                    attention_mask=batch['attention_mask'].to(device))
        loss = out.loss
        loss.backward()
        if (step + 1) % args.grad_accum == 0:
            opt.step(); opt.zero_grad(set_to_none=True)
        step += 1
        lv = float(loss.detach().item())
        if step == 1 or step % 25 == 0:
            elapsed = time.time() - t0
            toks_s = (step * args.batch * args.seq) / max(elapsed, 1e-6)
            print('[step=' + str(step) + '] loss=' + str(round(lv,4)) +
                  ' lr=' + str(args.lr) + ' toks/s=' + str(round(toks_s,0)) +
                  ' elapsed_min=' + str(round(elapsed/60,2)), flush=True)
        if step == 1 and lv > 8.0:
            with open(ABORT_STATUS, 'w') as f: f.write('STEP1_LOSS='+str(lv)+'\n')
            wstatus('ABORT_STEP1')
            print('[r10 ABORT] step=1 loss=' + str(lv) + ' > 8.0', flush=True)
            sys.exit(2)
        if lv < best_loss: best_loss = lv
        if step % args.eval_every == 0:
            try:
                run_kr_gen(step)
            except Exception as e:
                print("[kr_gen SKIP] " + str(e), flush=True)
        if step % args.save_every == 0:
            save_dir = os.path.join(args.ckpt_dir, 'step_' + str(step))
            model.save_pretrained(save_dir)
            tok.save_pretrained(save_dir)
            meta = {'step': step, 'loss': lv, 'best_loss': best_loss,
                    'lr': args.lr, 'b1': False, 'base': args.base_dir,
                    'warm_start_from': args.adapter_dir}
            with open(os.path.join(save_dir, 'train_meta.json'), 'w') as f:
                json.dump(meta, f, indent=2)
            print('[save] step=' + str(step) + ' → ' + save_dir, flush=True)

wstatus('DONE')
print('[r10] DONE step=' + str(step) + ' best_loss=' + str(round(best_loss,4)), flush=True)
