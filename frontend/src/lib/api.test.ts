import { fetchDocuments } from "./api";

test("uses relative API paths so the dev proxy can serve backend requests", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => [],
  });
  vi.stubGlobal("fetch", fetchMock);

  await fetchDocuments();

  expect(fetchMock).toHaveBeenCalledWith("/documents");

  vi.unstubAllGlobals();
});
