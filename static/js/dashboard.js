const statusElements = {
  available: document.querySelector('#available-spaces'),
  indicator: document.querySelector('#occupancy-indicator'),
  label: document.querySelector('#occupancy-label'),
  max: document.querySelector('#max-capacity'),
  message: document.querySelector('#status-message'),
  occupied: document.querySelector('#occupied-spaces'),
  progress: document.querySelector('#occupancy-progress'),
  progressBar: document.querySelector('#occupancy-progress-bar'),
};

const feedback = document.querySelector('#feedback');
const entryForm = document.querySelector('#entry-form');
const exitForm = document.querySelector('#exit-form');
const paymentForm = document.querySelector('#payment-form');
const entrySubmit = document.querySelector('#entry-submit');
let entryAllowed = false;

async function requestJson(url, options = {}) {
  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error('Não foi possível ligar à aplicação. Verifique a ligação à rede.');
  }

  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error('A aplicação devolveu uma resposta inválida.');
  }

  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    throw new Error('A aplicação devolveu uma resposta inválida.');
  }

  if (!response.ok || body.error) {
    const errorMessage = typeof body.message === 'string'
      ? body.message
      : typeof body.error === 'string'
        ? body.error
        : body.error?.message;
    throw new Error(errorMessage || 'Não foi possível concluir o pedido.');
  }

  return body;
}

function getData(payload) {
  return payload.data && typeof payload.data === 'object' ? payload.data : payload;
}

function displayFeedback(message, isError = false) {
  feedback.textContent = message;
  feedback.className = `rounded-xl p-4 text-sm ${
    isError
      ? 'bg-red-50 text-red-800 ring-1 ring-red-200'
      : 'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200'
  }`;
}

function hideFeedback() {
  feedback.className = 'hidden rounded-xl p-4 text-sm';
  feedback.textContent = '';
}

function setLoading(form, isLoading) {
  for (const control of form.querySelectorAll('button, input, select')) {
    control.disabled = isLoading;
  }
}

async function refreshStatus() {
  statusElements.message.textContent = 'A carregar lotação…';

  try {
    const response = await requestJson('/api/status');
    const status = getData(response);
    const occupied = status.occupied_spaces ?? status.occupiedSpaces;
    const capacity = status.max_capacity ?? status.maxCapacity;
    const available = status.available_spaces
      ?? status.availableSpaces
      ?? (
        Number.isSafeInteger(capacity) && Number.isSafeInteger(occupied)
          ? capacity - occupied
          : NaN
      );

    if (
      !Number.isSafeInteger(occupied)
      || !Number.isSafeInteger(capacity)
      || !Number.isSafeInteger(available)
      || capacity <= 0
      || occupied < 0
      || occupied > capacity
      || available < 0
      || available > capacity
      || occupied + available !== capacity
    ) {
      throw new Error('A resposta de lotação do Xano não contém valores válidos.');
    }

    const percentage = Math.min(100, (occupied / capacity) * 100);
    const full = available === 0;
    const level = percentage >= 100 ? 'full' : percentage >= 80 ? 'busy' : 'available';
    const colors = {
      available: {
        dot: 'bg-emerald-500',
        bar: 'bg-emerald-500',
        text: 'text-emerald-700',
        label: 'Disponível',
      },
      busy: {
        dot: 'bg-amber-500',
        bar: 'bg-amber-500',
        text: 'text-amber-700',
        label: 'Ocupação elevada',
      },
      full: {
        dot: 'bg-red-600',
        bar: 'bg-red-600',
        text: 'text-red-700',
        label: 'Parque cheio',
      },
    };
    const color = colors[level];

    statusElements.occupied.textContent = String(occupied);
    statusElements.available.textContent = String(available);
    statusElements.max.textContent = String(capacity);
    statusElements.indicator.className = `h-4 w-4 rounded-full ${color.dot}`;
    statusElements.label.className = `font-semibold ${color.text}`;
    statusElements.label.textContent = color.label;
    statusElements.progressBar.className = `h-full rounded-full transition-all ${color.bar}`;
    statusElements.progressBar.style.width = `${percentage}%`;
    statusElements.progress.setAttribute('aria-valuenow', String(Math.round(percentage)));
    statusElements.message.textContent = full
      ? 'Lotação esgotada. Não é possível registar novas entradas.'
      : `${available} ${available === 1 ? 'lugar disponível' : 'lugares disponíveis'}.`;
    entryAllowed = !full;
    entrySubmit.disabled = !entryAllowed;
    entrySubmit.title = full ? 'O parque está cheio.' : '';
  } catch (error) {
    statusElements.message.textContent = error.message;
    statusElements.occupied.textContent = '—';
    statusElements.available.textContent = '—';
    statusElements.max.textContent = '—';
    statusElements.progressBar.style.width = '0%';
    statusElements.progress.setAttribute('aria-valuenow', '0');
    statusElements.indicator.className = 'h-4 w-4 rounded-full bg-slate-400';
    statusElements.label.className = 'font-semibold text-slate-600';
    statusElements.label.textContent = 'Indisponível';
    entryAllowed = false;
    entrySubmit.disabled = true;
  }
}

entryForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  hideFeedback();
  if (!entryAllowed) {
    displayFeedback('Atualize a lotação antes de registar uma entrada.', true);
    return;
  }
  const formData = new FormData(entryForm);
  setLoading(entryForm, true);

  try {
    const response = await requestJson('/api/entries', {
      method: 'POST',
      body: JSON.stringify({
        plate: formData.get('plate').trim().toUpperCase(),
        vehicle_type: formData.get('vehicle_type'),
      }),
    });
    const entry = getData(response);
    displayFeedback(
      `Entrada registada para ${entry.plate || formData.get('plate').trim().toUpperCase()}.`,
    );
    entryForm.reset();
    await refreshStatus();
  } catch (error) {
    displayFeedback(error.message, true);
    await refreshStatus();
  } finally {
    setLoading(entryForm, false);
    entrySubmit.disabled = !entryAllowed;
    document.querySelector('#entry-plate').focus();
  }
});

exitForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  hideFeedback();
  const formData = new FormData(exitForm);
  const plate = formData.get('plate').trim().toUpperCase();
  setLoading(exitForm, true);

  try {
    const response = await requestJson('/api/exits', {
      method: 'POST',
      body: JSON.stringify({ plate }),
    });
    const exit = getData(response);
    const totalCents = exit.total_cents ?? exit.totalAmountCents;
    const formattedTotal = Number.isSafeInteger(totalCents) && totalCents >= 0
      ? new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' })
        .format(totalCents / 100)
      : null;

    displayFeedback(
      formattedTotal
        ? `Saída registada para ${exit.plate || plate}. Valor a pagar: ${formattedTotal}. A vaga mantém-se ocupada até à confirmação do pagamento.`
        : `Saída registada para ${exit.plate || plate}. A vaga mantém-se ocupada até à confirmação do pagamento.`,
    );
    exitForm.reset();
    const recordId = exit.record_id ?? exit.id;
    if (Number.isInteger(recordId)) {
      document.querySelector('#record-id').value = String(recordId);
    }
    await refreshStatus();
  } catch (error) {
    displayFeedback(error.message, true);
  } finally {
    setLoading(exitForm, false);
    document.querySelector('#entry-plate').focus();
  }
});

paymentForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  hideFeedback();
  const recordId = Number(new FormData(paymentForm).get('record_id'));
  setLoading(paymentForm, true);

  try {
    const response = await requestJson('/api/payments/confirm', {
      method: 'POST',
      body: JSON.stringify({ record_id: recordId }),
    });
    const payment = getData(response);
    if (payment.status !== 'Concluído') {
      throw new Error('A resposta não confirma a conclusão do pagamento.');
    }
    displayFeedback(
      `Pagamento confirmado${payment.plate ? ` para ${payment.plate}` : ''}. O lugar foi libertado.`,
    );
    paymentForm.reset();
    await refreshStatus();
  } catch (error) {
    displayFeedback(error.message, true);
  } finally {
    setLoading(paymentForm, false);
    document.querySelector('#entry-plate').focus();
  }
});

document.querySelector('#refresh-status').addEventListener('click', refreshStatus);
refreshStatus();
